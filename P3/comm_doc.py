
from quanser.common import GenericError
import socket
from urllib.parse import urlsplit



class StreamError(GenericError):
    """A stream exception derived from ``GenericError``.

    Example
    -------
    Read data from the first two analog input channels until the user aborts via a keyboard interrupt or there is an
    exception, such as loss of communication.

    >>> from quanser.communications import Stream, StreamError
    >>> stream = Stream()
    >>> stream.connect("tcpip://localhost:5000", False, 64, 64)
    >>> try:
    ...     stream.close()
    ...     stream.flush()  # Raises an exception: Cannot use a stream after it is closed.
    ... except StreamError as e:
    ...     print(e.get_error_message())  # Handle stream errors.
    ...

    """
    pass


class PollFlag:
    """A bit mask indicating the conditions for which to check during a `poll`."""
    __slots__ = ()

    RECEIVE = 0x01
    """On a listening stream, check for connections pending from clients. On a client stream, check whether there is any
    data available to receive."""

    SEND = 0x02
    """Not valid on a listening stream. On a client stream, check whether there is space in the stream buffer to store
    any data."""

    ACCEPT = 0x04
    """Not valid on a client stream. On a listening stream, check whether there is a pending client connection."""

    CONNECT = 0x08
    """Not valid on a listening stream. On a client stream, check whether the connection has completed."""

    FLUSH = 0x80
    """Not valid on a listening stream. On a client stream, check whether it is possible to flush any more data without
    blocking."""


class Timeout:
    """A structure to hold timeout information for the stream's `poll` function.

    Parameters
    ----------
    seconds : int
        The seconds portion of the timeout.
    nanoseconds : int
        The nanoseconds portion of the timeout.
    is_absolute : boolean
        Indicates whether the timeout is a relative timeout or an absolute timeout.

    Examples
    --------
    Create a 20-second timeout

    >>> from quanser.communications import Timeout
    >>> timeout = Timeout(20)

    Create a 2000-nanosecond timeout

    >>> from quanser.communications import Timeout
    >>> timeout = Timeout(nanoseconds=2000)

    Create a 1.02 second absolute timeout

    >>> from quanser.communications import Timeout
    >>> timeout = Timeout(1, 20000000, True)

    """
    def __init__(self, seconds=0, nanoseconds=0, is_absolute=False):
        self.seconds = seconds
        self.nanoseconds = nanoseconds
        self.is_absolute = is_absolute


class Stream:
    """A Python wrapper for the Quanser Stream API.

       Example
       -------
       >>> from quanser.communications import Stream
       >>> stream = Stream()

       """

    # region Life Cycle

    def __init__(self):
        self.sock : socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = socket.socket()
        self.bound = False

    # endregion

    # region Implementation

    def connect(self, uri, non_blocking, send_buffer_size, receive_buffer_size):
        """Connects to a listening stream referenced by the given URI. The URI specifies the protocol, address, port,
        and options associated with the stream. The Stream API uses the protocol to load a protocol-specific driver.

        URI examples::

            tcpip://remotehost:17000                        - connect to remote host on port 17000 using TCP/IP
            shmem://mymemory:1?bufsize=8192                 - connect via an 8K shared memory buffer
            pipe:mypipe?bufsize=4096                        - connect via a 4K named pipe
            i2c://localhost:0?baud='100000';address='0x48'  - connect via I2C at a baud rate of 100000

        If the non_blocking flag is set to ``False``, then this function will block until the connection is made.
        If the non_blocking flag is set to ``True``, then this function will not block. If the connection cannot be
        completed immediately, then ``-QERR_WOULD_BLOCK`` is raised. In this case, the connection may be completed using
        `poll` with the ``PollFlag.CONNECT`` flag.

        Parameters
        ----------
        uri : string
            A URI indicating the listening stream to which to connect.

        non_blocking : boolean
            Set to True to make the client connection non-blocking.

        send_buffer_size : int
            The size of the buffer to use for sending data over the stream, in bytes

        receive_buffer_size : int
            The size of the buffer to use for receiving data over the stream, in bytes

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Returns
        -------
        bool
            ``True`` if connected; ``False`` if connection in progress.

        Example
        -------
        >>> from quanser.communications import Stream
        >>> stream = Stream()
        >>> is_connected = stream.connect("tcpip://localhost:5039", False, 64, 64)
        >>> # ...
        ...
        >>> stream.shutdown()
        >>> stream.close()

        """
        # if self._stream is not None:
        #     self.close()
        #
        # client_stream = ffi.new("t_stream *")
        #
        # result = communications_lib.stream_connect(uri.encode('utf-8'),
        #                                            b'\x01' if non_blocking else b'\x00',
        #                                            send_buffer_size,
        #                                            receive_buffer_size,
        #                                            client_stream)
        #
        # if result < 0 and result != -_WOULD_BLOCK:
        #     raise StreamError(result)
        #
        # self._stream = client_stream[0]
        #
        # return result != -_WOULD_BLOCK
        raise NotImplementedError("Pi Simulator: Can't call connect directly")



    def listen(self, uri, non_blocking):
        """Establishes a server stream which listens on the given URI. The URI specifies the protocol, address, port and
        options associated with the server stream. The Stream API uses the protocol to load a protocol-specific driver.
        For example:

        tcpip://localhost:17000             - listen on port 17000 using TCP/IP
        shmem://mymemory:1?bufsize=8192     - listen via shared memory buffer. Use 8K buffers by default.
        pipe:mypipe?bufsize=4096            - listen via a named pipe. Use 4K buffers for the pipe.

        Parameters
        ----------
        uri : string
            A URI indicating the stream on which to listen.

        non_blocking : bool
            Set to True to prevent stream_accept calls from blocking.

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Example
        -------
        >>> from quanser.communications import Stream
        >>> stream = Stream()
        >>> stream.listen("tcpip://localhost:5039", False)
        >>> # ...
        ...
        >>> stream.shutdown()
        >>> stream.close()

        """
        # server_stream = ffi.new("t_stream *")
        #
        # result = communications_lib.stream_listen(uri.encode('utf-8'),
        #                                           b'\x01' if non_blocking else b'\x00',
        #                                           server_stream)
        #
        # if result < 0:
        #     raise StreamError(result)
        #
        # self._stream = server_stream[0]

        if self.bound:
            raise RuntimeError()

        url_s = urlsplit(uri)
        if url_s.scheme != "tcpip":
            raise ValueError("Pi simulator only allows TCP connections")
        if not non_blocking:
            raise ValueError("non_blocking has to be true")

        self.sock.setblocking(True)
        self.sock.bind((url_s.hostname, url_s.port))
        self.bound = True

    def accept(self, send_buffer_size, receive_buffer_size):
        """Accepts a connection to a listening communication stream by a client. The client connects using
        `connect`.

        If `listen` was called with `non_blocking` set to ``False``, then this call will block until a client connects.
        The client stream returned will also be a blocking stream.

        If `listen` was called with non_blocking set to ``True``, then this call will not block. If there is no pending
        client connection, then it will raise `-QERR_WOULD_BLOCK`. The `poll` function may be used with
        ``PollFlag.ACCEPT`` to determine when a client connection is pending. In this case, the client stream returned
        will also be a non-blocking stream.

        On POSIX systems this function should be interruptible by a signal so that arrival of a signal will cause a
        ``-QERR_INTERRUPTED`` error to be returned.

        Parameters
        ----------
        send_buffer_size : int
            The size of the buffer to use for sending data over the stream, in bytes

        receive_buffer_size : int
            The size of the buffer to use for receiving data over the stream, in bytes

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Returns
        -------
        Stream or None
            The client stream or ``None`` if there is no client stream.

        Example
        -------
        >>> from quanser.communications import Stream
        >>> uri = "tcpip://localhost:5000"
        >>> send_buffer_size = 64
        >>> receive_buffer_size = 64
        >>> server_stream = Stream()
        >>> client_stream = Stream()
        >>> server_stream.listen(uri, False)
        >>> client_stream.connect(uri, False, send_buffer_size, receive_buffer_size)
        >>> client_connection = server_stream.accept(send_buffer_size, receive_buffer_size)
        >>> # ...
        ...
        >>> client_connection.shutdown()
        >>> client_stream.shutdown()
        >>> client_connection.close()
        >>> client_stream.close()
        >>> server_stream.close()

        """
        # client_stream = Stream()
        #
        # _client_stream = ffi.new("t_stream *")
        #
        # result = communications_lib.stream_accept(self._stream if self._stream is not None else ffi.NULL,
        #                                           send_buffer_size,
        #                                           receive_buffer_size,
        #                                           _client_stream)
        #
        # if result == -_WOULD_BLOCK:
        #     return None
        #
        # if result < 0:
        #     raise StreamError(result)
        #
        # client_stream._stream = _client_stream[0]
        # return client_stream
        return self

    def poll(self, timeout, flags):
        """Polls the stream to determine whether it is possible to send or receive or accept a connection without
        blocking. The flags argument determines the conditions for which to check. The return value indicates the
        conditions which occurred. This function returns after the given timeout with a value of 0 if none of the
        conditions occurs. If an error occurs, then it returns a negative error code. The function will return before
        the timeout if at least one of the conditions occurs prior to the timeout.

        Note that this function may return zero even if the timeout has not occurred, even when the timeout is infinite.
        This special case occurs when the `shutdown` method has been called on the stream. Once the stream is shut down,
        the timeout may be limited to the close timeout associated with the stream (for shmem, for instance). Hence,
        the stream may timeout in this  case and return 0 before the specified timeout, even if the timeout is infinite.

        Parameters
        ----------
        timeout : Timeout
            A timeout structure.

        flags : int
            A bit mask indicating the conditions for which to check. Valid flags are:
            ``PollFlag.RECEIVE`` = on a listening stream, check for connections pending from clients. On a client
            stream, check whether there is any data available to receive.
            ``PollFlag.SEND`` = not valid on a listening stream. On a client stream, check whether there is space in
            the stream buffer to store any data.
            ``PollFlag.FLUSH` = not valid on a listening stream. On a client stream, check whether it is possible to
            flush any more data without blocking.
            ``PollFlag.ACCEPT`` = not valid on a client stream. On a listening stream, check whether there is a pending
            client connection.
            ``PollFlag.CONNECT`` = not valid on a listening stream. On a client stream, check whether the connection
            has completed.

        Returns
        -------
        int
            A bit mask containing the conditions which were satisfied. It has the same definition as the flags argument.
            If none of the specified conditions occurs before the timeout, then 0 is returned.

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Example
        -------
        Poll a stream

        >>> from quanser.communications import Stream, PollFlag
        >>> timeout = Timeout(3)
        >>> stream = Stream()
        >>> stream.connect("tcpip://localhost:5000", False, 64, 64)
        >>> result = stream.poll(timeout, PollFlag.SEND | PollFlag.RECEIVE)
        >>> # ...
        ...
        >>> stream.shutdown()
        >>> stream.close()

        """
        # _timeout = None
        # if timeout is not None:
        #     _timeout = ffi.new("const t_timeout *")
        #     _timeout.seconds = timeout.seconds
        #     _timeout.nanoseconds = timeout.nanoseconds
        #     _timeout.is_absolute = b'\x01' if timeout.is_absolute else b'\x00'
        # else:
        #     _timeout = ffi.NULL
        #
        # result = communications_lib.stream_poll(self._stream if self._stream is not None else ffi.NULL, _timeout, flags)
        #
        # if result < 0:
        #     raise StreamError(result)
        if flags != PollFlag.ACCEPT:
            raise ValueError("Only accepting a comm is allowed")

        self.sock.listen()
        self.conn, addr = self.sock.accept()
        print(f"Accepted connection from {addr}")
        result = PollFlag.ACCEPT
        return result

    def shutdown(self):
        """Shuts down send and/or receives in preparation for closing the stream.

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Example
        -------
        >>> from quanser.communications import Stream
        >>> stream = Stream()
        >>> stream.connect("tcpip://localhost:5000", False, 64, 64)
        >>> # ...
        ...
        >>> stream.shutdown()
        >>> stream.close()

        """
        # result = communications_lib.stream_shutdown(self._stream if self._stream is not None else ffi.NULL)
        #
        # if result < 0:
        #     raise StreamError(result)
        self.sock.close()
        self.sock.shutdown(socket.SHUT_RDWR)

    def close(self):
        """Closes the stream. All resources associated with the stream are freed.

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Example
        -------
        >>> from quanser.communications import Stream
        >>> stream = Stream()
        >>> stream.connect("tcpip://localhost:5000", False, 64, 64)
        >>> # ...
        ...
        >>> stream.shutdown()
        >>> stream.close()

        """
        # result = communications_lib.stream_close(self._stream if self._stream is not None else ffi.NULL)
        #
        # if result < 0:
        #     raise StreamError(result)
        #
        # self._stream = None
        self.conn.close()

    @staticmethod
    def close_all():
        """Closes all streams established using stream_listen, stream_connect or stream_accept.

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Example
        -------
        >>> from quanser.communications import Stream
        >>> uri = "tcpip://localhost:5000"
        >>> server = Stream()
        >>> client = Stream()
        >>> server.listen(uri, False)
        >>> client.connect(uri, False, 64, 64)
        >>> # ...
        ...
        >>> Stream.close_all()

        """
        # result = communications_lib.stream_close_all()
        #
        # if result < 0:
        #     raise StreamError(result)
        raise NotImplementedError

    def get_boolean_property(self, properties, num_properties, buffer):
        raise NotImplementedError

    def set_boolean_property(self, properties, num_properties, buffer):
        raise NotImplementedError

    def send(self, buffer, buffer_size):
        """Writes data to the stream buffer. It attempts to store `buffer_size` bytes in the stream buffer. If there is
        enough room available in the stream buffer, then it stores the data in the buffer and returns immediately. The
        data is not written to the actual communication channel until the stream is flushed using `flush` or there is no
        more room available in the stream buffer. If an error occurs, then an exception is raised. If the connection is
        closed, it is considered an error condition.

        If `listen` or `connect` was called with the non-blocking flag set to ``False``, then this function may block
        attempting to flush the stream buffer. All the data will be consumed and the total number of bytes sent is
        returned. Some of the data may remain in the stream buffer and not be sent until the next time `flush` is called
        or there is no more room available in the stream buffer. If an error occurs, then an exception is raised and the
        stream should be closed.

        If `listen` or `connect` was called with the non-blocking flag set to ``True``, then this function does not
        block. It returns the number of bytes sent successfully, which will be between 1 and `buffer_size` (unless
        `buffer_size` is zero). If no bytes could be sent without blocking, then the function raises an exception with
        ``-QERR_WOULD_BLOCK``. If an error occurs, then an exception is raised and the stream should be closed.

        This function does not support two threads calling `send` or `flush` at the same time; however, `send` or
        `flush` may be called by another thread at the same time as `receive`.

        The semantics of this function are comparable to the BSD `send()` socket function.

        Parameters
        ----------
        buffer : array_like
            A buffer of at least `buffer_size` bytes containing the data to be sent.
        buffer_size : int
            The number of bytes to send from the buffer.

        Returns
        -------
        int
            The number of bytes sent, which may be less than `buffer_size` bytes for non-blocking streams. If an error
            occurs, then an exception is raised. A value of zero is only returned if `buffer_size` is zero.

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Examples
        --------

        Send a text message immediately by writing it to the stream and then flushing the buffer.

        >>> from quanser.communications import Stream
        >>> message = "Hello".encode()
        >>> num_bytes = len(message)
        >>> stream = Stream()
        >>> stream.connect("tcpip://localhost:5000", False, 64, 64)
        >>> bytes_written = stream.send(message, num_bytes)
        >>> stream.flush()
        >>> # ...
        ...
        >>> stream.shutdown()
        >>> stream.close()

        Send 2 doubles immediately by writing them to the stream and then flushing the buffer.

        >>> import struct
        >>> from quanser.communications import Stream
        >>> data = bytearray(struct.pack("!dd", 1.2, 3.4))
        >>> num_bytes = len(data)
        >>> stream = Stream()
        >>> stream.connect("tcpip://localhost:5000", False, 64, 64)
        >>> bytes_written = stream.send(data, num_bytes)
        >>> stream.flush()
        >>> # ...
        ...
        >>> stream.shutdown()
        >>> stream.close()

        """
        # result = communications_lib.stream_send(self._stream if self._stream is not None else ffi.NULL,
        #                                         ffi.from_buffer(buffer) if buffer is not None else ffi.NULL,
        #                                         buffer_size)
        #
        # if result < 0:
        #     raise StreamError(result)
        #
        # return result
        if len(buffer) > buffer_size:
            raise ValueError("buffer size inappropriate")
        self.conn.sendall(buffer)

    def receive(self, buffer, buffer_size):
        """Receives data over a client stream. It attempts to receive `buffer_size` bytes from the communication
        channel.

        If `listen` or `connect` was called with the non-blocking flag set to ``False``, then this function blocks until
        all the data is read. If the connection has been closed gracefully, then it returns 0 only once there is no more
        data to receive. Otherwise it returns the number of bytes read before the connection closed. Once all the data
        in the stream buffer is exhausted, it will return 0 to indicate the connection has been closed. If an error
        occurs, then it raises an exception.

        If `listen` or `connect` was called with the non-blocking flag set to ``True``, then this function does not
        block. If no data is available at all, then it raises `-QERR_WOULD_BLOCK`. In this case, the `poll` function
        may be used with ``PollFlag.STREAM`` to determine when data becomes available; otherwise, it returns the number
        of bytes received.

        Unlike the `receive_byte_array` function, this function does not require that the stream receive buffer be at
        least `buffer_size` bytes in length. Hence, it allows smaller stream buffers to be used.

        This function does not support two threads calling `receive` at the same time; however, `send` or `flush` may be
        called by another thread at the same time as `receive`.

        The semantics of this function differ from the BSD `recv()` socket function because it receives `buffer_size`
        bytes in blocking mode rather than the number of bytes that were sent in a single `send()` call at the peer. The
        semantics differ because this function attempts to "read ahead" by keeping the stream buffer full, thereby
        minimizing the number of receive operations performed on the internal connection. Also, due to buffering of the
        `send` operation, the number of `send()` calls made at the peer may not correspond to the number expected.

        Parameters
        ----------
        buffer : array_like
            A buffer of at least `buffer_size` bytes in which the received data will be stored.
        buffer_size : int
            The number of bytes available in the buffer.

        Returns
        -------
        int
            The number of bytes received, which may be less than `buffer_size` bytes for non-blocking streams. If no
            more data is available and the connection has been closed gracefully, then 0 is returned. If an error
            occurs, then an exception is raised.

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Example
        -------

        >>> from quanser.communications import Stream
        >>> buffer_size = 64
        >>> buffer = bytearray(buffer_size)
        >>> stream = Stream()
        >>> stream.connect("tcpip://localhost:5000", False, buffer_size, buffer_size)
        >>> bytes_read = stream.receive(buffer, buffer_size)
        >>> # ...
        ...
        >>> stream.shutdown()
        >>> stream.close()

        """
        # result = communications_lib.stream_receive(self._stream if self._stream is not None else ffi.NULL,
        #                                            ffi.from_buffer(buffer) if buffer is not None else ffi.NULL,
        #                                            buffer_size)
        #
        # if result < 0:
        #     raise StreamError(result)
        #
        # return result
        return self.conn.recv_into(buffer, nbytes=buffer_size)

    def flush(self):
        """Flushes the stream buffer. It attempts to send the contents of the buffer over the communication channel. If
        an error occurs, then it raises an exception. If the connection is closed, it is considered an error condition.

        If `listen` or `connect` was called with the non-blocking flag set to ``False``, then this function blocks until
        all the data in the buffer is sent.

        If `listen` or `connect` was called with the non-blocking flag set to ``True``, then this function does not
        block. It attempts to send all the data remaining in the stream buffer. However, if this operation would block,
        then it raises ``-QERR_WOULD_BLOCK``, even if it has already sent some of the data. In this case, the `poll`
        function may be used with ``PollFlag.FLUSH`` to determine when at least one more bytes may be flushed.

        This function does not support two threads calling `send` or `flush` at the same time; however, `send` or
        `flush` may be called by another thread at the same time as `receive`.

        Raises
        ------
        StreamError
            On non-zero return code. A suitable error message may be retrieved using `get_error_message`.

        Example
        -------
        Flush the send buffer in order to send a message that is smaller than the size of the buffer.

        >>> from quanser.communications import Stream
        >>> message = "Hello".encode()
        >>> num_bytes = len(message)
        >>> send_buffer_size = 64
        >>> receive_buffer_size = 64
        >>> stream = Stream()
        >>> stream.connect("tcpip://localhost:5000", False, send_buffer_size, receive_buffer_size)
        >>> bytes_written = stream.send(message, num_bytes)
        >>> stream.flush()
        >>> stream.shutdown()
        >>> stream.close()

        """
        # result = communications_lib.stream_flush(self._stream if self._stream is not None else ffi.NULL)
        #
        # if result < 0:
        #     raise StreamError(result)
        pass
