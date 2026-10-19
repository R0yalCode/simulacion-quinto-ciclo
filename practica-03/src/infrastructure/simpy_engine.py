"""Adaptador de SimPy: eventos y estadísticas observables de una sola estación FIFO."""
import random
import simpy
from domain.models import Config


class MM1Engine:
    def run(self, config: Config) -> dict:
        config.validate()
        rng = random.Random(config.seed)
        env = simpy.Environment()
        server = simpy.Resource(env, capacity=1)
        events = []
        arrived = completed = 0
        total_wait = total_system = total_service = 0.0
        queue_area = system_area = busy_area = 0.0
        previous_time = 0.0
        previous_queue = previous_system = previous_busy = 0
        wait_samples = []
        jobs = []

        def emit(kind, job_id=None, wait=None, service=None):
            nonlocal queue_area, system_area, busy_area, previous_time
            nonlocal previous_queue, previous_system, previous_busy
            dt = max(0.0, env.now - previous_time)
            queue_area += dt * previous_queue
            system_area += dt * previous_system
            busy_area += dt * previous_busy
            previous_time = float(env.now)
            previous_queue = len(server.queue)
            previous_busy = int(server.count > 0)
            previous_system = arrived - completed
            t = float(env.now)
            events.append({
                't': round(t, 7), 'type': kind, 'id': job_id,
                'queue': previous_queue, 'system': previous_system,
                'busy': previous_busy, 'arrived': arrived, 'completed': completed,
                'mean_wait': total_wait / completed if completed else 0.0,
                'mean_system': total_system / completed if completed else 0.0,
                'mean_service': total_service / completed if completed else 0.0,
                'avg_queue': queue_area / t if t else 0.0,
                'avg_system': system_area / t if t else 0.0,
                'utilization': busy_area / t if t else 0.0,
                'throughput': completed / t if t else 0.0,
                'wait': wait, 'service': service,
            })

        def customer(jid):
            nonlocal arrived, completed, total_wait, total_system, total_service
            arrival = env.now
            arrived += 1
            with server.request() as request:
                emit('arrival', jid)
                yield request
                wait = float(env.now - arrival)
                service = rng.expovariate(config.service_rate)
                emit('service_start', jid, wait=wait, service=service)
                yield env.timeout(service)
            # Tras liberar el recurso, contar la salida sin dobles conteos.
            completed += 1
            total_wait += wait
            total_system += env.now - arrival
            total_service += service
            wait_samples.append(wait)
            jobs.append({'id': jid, 'arrival': arrival, 'start': arrival + wait,
                         'departure': float(env.now), 'wait': wait, 'service': service,
                         'system': float(env.now - arrival)})
            emit('departure', jid, wait=wait, service=service)

        def source():
            jid = 0
            while True:
                delay = rng.expovariate(config.arrival_rate)
                if env.now + delay >= config.duration:
                    return
                yield env.timeout(delay)
                jid += 1
                env.process(customer(jid))

        env.process(source())
        env.run(until=config.duration)
        emit('end')
        return {
            'events': events,
            'jobs': jobs,
            'summary': {
                'arrived': arrived, 'completed': completed,
                'pending': arrived - completed,
                'mean_wait': total_wait / completed if completed else 0,
                'mean_system': total_system / completed if completed else 0,
                'mean_service': total_service / completed if completed else 0,
                'avg_queue': queue_area / config.duration,
                'avg_system': system_area / config.duration,
                'utilization': busy_area / config.duration,
                'throughput': completed / config.duration,
                'max_queue': max((e['queue'] for e in events), default=0),
                'wait_samples': wait_samples,
            },
        }
