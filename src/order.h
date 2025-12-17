#ifndef ORDER_H
#define ORDER_H

// Define the orders that can be sent and received
enum Order {
  HELLO = 0x30,
  DELTA = 0x31,
  OFFSET = 0x32,
  ALREADY_CONNECTED = 0x33,
  ERROR = 0x34,
  RECEIVED = 0x35,
  FULL = 0x36,
  REGUL = 0x37,
  STATUS = 0x38,
  SAVE = 0x39,
};

typedef enum Order Order;

// If DEBUG is set to true, the arduino will send back all the received messages
#define DEBUG false

#define DEBUG_PROTO false

#endif
