import asyncio
import sys


async def timed_input(prompt, timeout=0):
    """Wait for input from the user
    Note that user input is not available until the user pressed the enter or
    return key.
    Arguments:
        prompt  - text that is used to prompt the users response
        timeout - the number of seconds to wait for input
    Raises:
        An asyncio.futures.TimeoutError is raised if the user does not provide
        input within the specified timeout period.
    Returns:
        A string containing the users response
    """
    # Write the prompt to stdout
    print(prompt, flush=True)

    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    # The response callback will receive the users input and put it onto the
    # queue in an independent task.
    def response():
        loop.create_task(queue.put(sys.stdin.readline()))

    # Create a reader so that the response callback is invoked if the user
    # provides input on stdin.
    loop.add_reader(sys.stdin.fileno(), response)

    try:
        # Wait for an item to be placed on the queue. The only way this can
        # happen is if the reader callback is invoked.
        return (await asyncio.wait_for(queue.get(), timeout=timeout)).rstrip("\n")

    except asyncio.TimeoutError:
        # Make sure that any output to stdout or stderr that happens following
        # this coroutine, happens on a new line.
        sys.stdout.write('\n')
        sys.stdout.flush()

    finally:
        # Whatever happens, we should remove the reader so that the callback
        # never gets called.
        loop.remove_reader(sys.stdin.fileno())
