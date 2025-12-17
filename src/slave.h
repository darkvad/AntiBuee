#ifndef ARDUINO_SLAVE_H
#define ARDUINO_SLAVE_H

/*!
 * \brief Update the temperature offset for the onboard sensor
 */
void update_delta_temp(uint8_t delta);

/*!
 * \brief Update the temperature offset for the onboard sensor
 */
void update_setpoint_offset(uint8_t offset);

/*!
 * Set the full power
 */
void full();

/*!
 * Set the regulated power
 */
void regul();


/*!
 * \brief Read one byte from the serial and cast it to an Order
 * \return the order received
 */
Order read_order();

/*!
 * \brief Wait until there are enough bytes in the buffer
 * \param num_bytes the number of bytes
 * \param timeout (ms) The timeout, time after which we release the lock
 * even if there are not enough bytes
 */
void wait_for_bytes(int num_bytes, unsigned long timeout);

/*!
 * \brief Read one byte from a serial port and convert it to a 8 bits int
 * \return the decoded number
 */
uint8_t read_i8();

/*!
 * \brief Read two bytes from a serial port and convert it to a 16 bits int
 * \return the decoded number
 */
uint16_t read_i16();


/*!
 * \brief Send one order (one byte)
 * \param order type of order
 */
void write_order(enum Order order);

/*!
 * \brief Write one byte int to serial port (between -127 and 127)
 * \param num an int of one byte
 */
void write_i8(uint8_t num);

/*!
 * \brief Send a two bytes signed int via the serial
 * \param num the number to send (max: (2**16/2 -1) = 32767)
 */
void write_i16(uint16_t num);

/*!
 * \brief Listen the serial and decode the message received
 */
void get_messages_from_serial();

void printValues(float steinhart);
#endif
