from contextlib import contextmanager
from sshtunnel import SSHTunnelForwarder

@contextmanager
def ssh_tunnel(ssh_host: str, ssh_port: int, ssh_user: str, ssh_key_path: str,
               remote_host: str, remote_port: int):
    """
    Creates a local port forwarding tunnel:
    localhost:<auto> -> remote_host:remote_port (through ssh_host)
    """
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=ssh_key_path,
        remote_bind_address=(remote_host, remote_port),
        local_bind_address=("127.0.0.1", 0),
    ) as tunnel:
        yield tunnel
