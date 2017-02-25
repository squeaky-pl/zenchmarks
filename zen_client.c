#include <uv.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>
#include <string.h>


uv_loop_t* loop;


uv_buf_t buffers[] = {
  {.base = "A\n", .len = 2},
  {.base = "B\n", .len = 2},
  {.base = "C\n", .len = 2},
  {.base = "D\n", .len = 2},
  {.base = "E\n", .len = 2},
  {.base = "F\n", .len = 2},
  {.base = "G\n", .len = 2},
  {.base = "H\n", .len = 2},
  {.base = "I\n", .len = 2},
  {.base = "J\n", .len = 2},
  {.base = "K\n", .len = 2},
  {.base = "L\n", .len = 2},
  {.base = "M\n", .len = 2},
  {.base = "N\n", .len = 2},
  {.base = "O\n", .len = 2},
  {.base = "P\n", .len = 2},
  {.base = "Q\n", .len = 2},
  {.base = "R\n", .len = 2},
  {.base = "S\n", .len = 2},
  {.base = "T\n", .len = 2},
  {.base = "U\n", .len = 2},
  {.base = "V\n", .len = 2},
  {.base = "W\n", .len = 2},
  {.base = "X\n", .len = 2},
  {.base = "Y\n", .len = 2},
  {.base = "Z\n", .len = 2}
};


bool timeout = false;


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

  int requests = 0;
  for(char* ch = buf->base; ;requests++) {
    ch = memchr(ch, '\n', nread - (ch - buf->base));
    if(!ch)
      break;
    ch++;
  }

  connection->requests += requests;
  connection->idx += requests;
  while(connection->idx > 25)
    connection->idx -= 25;

  if(!timeout)
    uv_write(
      &connection->w_req, stream, &buffers[connection->idx], 1, on_write);
  else
    uv_read_stop(stream);
}


void alloc_cb(uv_handle_t* handle, size_t suggested_size, uv_buf_t* buf) {
  connection_t* connection = (connection_t*)handle->data;
  buf->base = connection->read_buf;
  buf->len = 1024;
}


void on_write(uv_write_t* req, int status) {
}


void on_connect(uv_connect_t *req, int status) {
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
}


int main(int argc, char* argv[])
{
  int duration = 2;
  int connection_num = 100;
  int opt;
  while((opt = getopt(argc, argv, "dc:")) != -1) {
    switch (opt) {
    case 'd':
       duration = atoi(optarg);
       break;
    case 'c':
       connection_num = atoi(optarg);
       break;
    default: /* '?' */
       fprintf(stderr, "Usage: %s [-d secs] \n",
               argv[0]);
       exit(1);
    }
  }

  loop = uv_default_loop();

  struct sockaddr_in dest;
  uv_ip4_addr("127.0.0.1", 8080, &dest);

  connection_t* connections = malloc(connection_num * sizeof(connection_t));

  for(int i = 0; i < connection_num; i++) {
    uv_tcp_t* socket = (uv_tcp_t*)malloc(sizeof(uv_tcp_t));
    uv_tcp_init(loop, socket);

    uv_connect_t* connect = (uv_connect_t*)malloc(sizeof(uv_connect_t));
    connect->data = &connections[i];

    uv_tcp_connect(connect, socket, (const struct sockaddr*)&dest, on_connect);
  }

  uv_timer_t t_req;
  uv_timer_init(loop, &t_req);
  uv_timer_start(&t_req, on_timer, duration * 1000, 0);

  uv_run(loop, UV_RUN_DEFAULT);

  unsigned long sum = 0;
  for(int i = 0; i < connection_num; i++)
    sum += connections[i].requests;

  printf("Requests: %ld\n", sum);

  return 0;
}
