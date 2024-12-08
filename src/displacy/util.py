import socket


def find_available_port(start: int, host: str, auto_select: bool = False) -> int:
    """Given a starting port and a host, handle finding a port.

    If `auto_select` is False, a busy port will raise an error.

    If `auto_select` is True, the next free higher port will be used.

    start (int): the port to start looking from
    host (str): the host to find a port on
    auto_select (bool): whether to automatically select a new port if the given
        port is busy (default False)
    RETURNS (int): The port to use.
    """
    if not _is_port_in_use(start, host):
        return start

    port = start
    if not auto_select:
        # raise ValueError(Errors.E1050.format(port=port))
        raise ValueError("error")

    while _is_port_in_use(port, host) and port < 65535:
        port += 1

    if port == 65535 and _is_port_in_use(port, host):
        raise ValueError("error")

    # if we get here, the port changed
    print("warning")
    return port


def _is_port_in_use(port: int, host: str = "localhost") -> bool:
    """Check if 'host:port' is in use. Return True if it is, False otherwise.

    port (int): the port to check
    host (str): the host to check (default "localhost")
    RETURNS (bool): Whether 'host:port' is in use.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
        return False
    except socket.error:
        return True
    finally:
        s.close()


def escape_html(text: str) -> str:
    """Replace <, >, &, " with their HTML encoded representation. Intended to
    prevent HTML errors in rendered displaCy markup.

    text (str): The original text.
    RETURNS (str): Equivalent text to be safely used within HTML.
    """
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text
