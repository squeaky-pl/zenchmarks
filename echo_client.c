#include <uv.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>


uv_loop_t* loop;

uv_buf_t buffers[] = {
  {.base = "A", .len = 1},
  {.base = "B", .len = 1},
  {.base = "C", .len = 1},
  {.base = "D", .len = 1},
  {.base = "E", .len = 1},
  {.base = "F", .len = 1},
  {.base = "G", .len = 1},
  {.base = "H", .len = 1},
  {.base = "I", .len = 1},
  {.base = "J", .len = 1},
  {.base = "K", .len = 1},
  {.base = "L", .len = 1},
  {.base = "M", .len = 1},
  {.base = "N", .len = 1},
  {.base = "O", .len = 1},
  {.base = "P", .len = 1},
  {.base = "Q", .len = 1},
  {.base = "R", .len = 1},
  {.base = "S", .len = 1},
  {.base = "T", .len = 1},
  {.base = "U", .len = 1},
  {.base = "V", .len = 1},
  {.base = "W", .len = 1},
  {.base = "X", .len = 1},
  {.base = "Y", .len = 1},
  {.base = "Z", .len = 1}
};


bool timeout;


typedef struct {
  unsigned long requests;
  size_t idx;
  uv_write_t w_req;
  uv_stream_t* stream;
  char read_buf[1024];
} connection_t;


void on_write(uv_write_t* req, int status);


void on_read(uv_stream_t* stream, ssize_t nread, const uv_buf_t* buf)
{
  connection_t* connection = (connection_t*)stream->data;
  connection->requests++;
  connection->idx++;
  if(connection->idx == 26)
    connection->idx = 0;

  if(!timeout) {
    uv_write(&connection->w_req, stream, &buffers[connection->idx], 1, on_write);
  } else {
    uv_read_stop(stream);
  }
}


void alloc_cb(uv_handle_t* handle, size_t suggested_size, uv_buf_t* buf) {
  connection_t* connection = (connection_t*)handle->data;
  buf->base = connection->read_buf;
  buf->len = 1024;
}


void on_write(uv_write_t* req, int status)
{
  if (status) {
    fprintf(stderr, "uv_write error: %s\n", uv_strerror(status));
    return;
  }
}


void on_connect(uv_connect_t *req, int status) {
    if (status < 0) {
        fprintf(stderr, "New connection error %s\n", uv_strerror(status));
        // error!
        return;
    }

    uv_stream_t* stream = req->handle;
    connection_t* connection = (connection_t*)req->data;
    connection->stream = stream;
    connection->requests = 0;
    connection->idx = 0;
    stream->data = connection;

    uv_read_start(stream, alloc_cb, on_read);
    uv_write(&connection->w_req, stream, &buffers[connection->idx], 1, on_write);
}


void on_timer(uv_timer_t* req)
{
  timeout = true;
  printf("on_timer\n");
}


int main(int argc, char* argv[])
{
  int duration = 50;
  int opt;
  while((opt = getopt(argc, argv, "d:")) != -1) {
    switch (opt) {
    case 'd':
       duration = atoi(optarg);
       break;
    default: /* '?' */
       fprintf(stderr, "Usage: %s [-d secs] \n",
               argv[0]);
       exit(1);
    }
  }

  loop = uv_default_loop();

  uv_tcp_t* socket = (uv_tcp_t*)malloc(sizeof(uv_tcp_t));
  uv_tcp_init(loop, socket);

  uv_connect_t* connect = (uv_connect_t*)malloc(sizeof(uv_connect_t));
  connect->data = malloc(sizeof(connection_t));

  struct sockaddr_in dest;
  uv_ip4_addr("127.0.0.1", 8080, &dest);

  uv_tcp_connect(connect, socket, (const struct sockaddr*)&dest, on_connect);

  uv_timer_t t_req;
  uv_timer_init(loop, &t_req);
  uv_timer_start(&t_req, on_timer, duration * 1000, 0);

  uv_run(loop, UV_RUN_DEFAULT);

  return 0;
}
