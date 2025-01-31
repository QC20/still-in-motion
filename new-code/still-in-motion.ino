/*
* Original by Jonas Kjeldmnd Jensen (Yunus), September 2024
* Modified for Weact 4.2" E-Paper Display
*/

#include <Arduino.h>
#include <SD.h>
#include <LowPower.h>
#include <SPI.h>
#include <EEPROM.h>
#include <avr/pgmspace.h>
#include "epd_adapter.h"
#include "read_bmp.h"
#include "eeprom_data.h"
#include "debug.h"
#include "picture_index.h"

// Definitions
#define PIN_POWER_SELECT    5
#define PIN_SD_CHIP_SELECT  6
#define PIN_MOSI            11
#define PIN_SCLK            13

#define SECONDS_IN_A_MINUTE  60
#define SECONDS_TO_DISPLAY   10  // wake time is 10 seconds
#define NUMBER_OF_SLEEP_LOOPS   ((10 * SECONDS_IN_A_MINUTE - SECONDS_TO_DISPLAY)/8)

// Function declarations
int get_next_file_handle(SDFile &sdFile);
inline void beginSpiTransaction() __attribute__((always_inline));
inline void endSpiTransaction() __attribute__((always_inline));
void sendQuarterRow(Epd *pEpd, char *buffer);

// Global variables
long sleep_loops = 0;

void setup() {
  Debug::serialBegin(9600);
  Debug::printEepromErrorInfo();

  int pictureIndex = EepromData::readPictureIndex();

  #ifdef SERIAL_DEBUG
  Debug::printProgMem(PSTR("Starting off from picture index "));
  Serial.print(pictureIndex, DEC);
  Serial.print("\r\n");
  #endif // SERIAL_DEBUG

  PictureIndex::setPictureIndex(pictureIndex);
}

void loop() {
  powerUpPeripherals();
  updateDisplayWithNewPicture();
  powerDownPeripherals();

  while(sleep_loops < NUMBER_OF_SLEEP_LOOPS) {
    Debug::printProgMem(PSTR("Sleeping\r\n"));

    Debug::serialFlush();
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF); 
    sleep_loops++;

    Debug::printProgMem(PSTR("Waking\r\n"));
  }
  sleep_loops = 0;
}

void updateDisplayWithNewPicture() {
  bool bmpFileInit = false;
  Epd epd;
  SDFile bmpFile;

  Debug::printProgMem(PSTR("epd.Init()\r\n"));
  if (epd.Init() != SUCCESS) {
    Debug::printProgMem(PSTR("e-Paper init failed.\r\n"));
    Debug::error(ERRORCODE_EPAPER_INIT_FAILED);
    return;
  }

  // Clear the display
  Debug::printProgMem(PSTR("e-Paper Clear\r\n"));
  beginSpiTransaction();
  epd.Clear(EPD_WHITE);
  endSpiTransaction();

  SD.begin(SPI_QUARTER_SPEED, PIN_SD_CHIP_SELECT);
  // getNextFileHandle has the error handling code in it
  if(getNextFileHandle(bmpFile) != SUCCESS) {
    goto cleanup;
  }
  bmpFileInit = true;

  Debug::printProgMem(PSTR("Display Image\r\n"));
  displayImage(&epd, bmpFile);

  delay(3000);

cleanup:  
  Debug::printProgMem(PSTR("EPaper Sleep...\r\n"));
  beginSpiTransaction();
  epd.Sleep();
  endSpiTransaction();

  if(bmpFileInit) {
    bmpFile.close();
  }

  SD.end();
  PictureIndex::updateInUsePictureIndex();
}

int displayImage(Epd * pEpd, SDFile & bmpFile) {
  int ret = SUCCESS;
  
  beginSpiTransaction();
  pEpd->SendCommand(0x10); // Start data transmission
  endSpiTransaction();

  // Create the ReadBMP class
  ReadBMP readbmp(&bmpFile);

  if (readbmp.parseHeader() != SUCCESS) {
    ret = FAILURE;
    goto display_image_cleanup;
  }

  if(readbmp.width() != EPD_WIDTH || readbmp.height() != EPD_HEIGHT) {
    Debug::printProgMem(PSTR("Invalid image size.\r\n"));
    Debug::error(ERRORCODE_BMP_INVALID_IMAGE_SIZE);
    ret = FAILURE;
    goto display_image_cleanup;
  }

  {
    char quarterLineBuffer[EPD_WIDTH/4];
    for(int row = 0; row < EPD_HEIGHT; row++) {
      for(int quarter = 0; quarter < 4; quarter++) {
        // Read in one quarter row of data
        if(readbmp.readQuarterLine(quarterLineBuffer) == FAILURE) {
          ret = FAILURE;
          goto display_image_cleanup;
        }

        beginSpiTransaction();
        // Write out one quarter row to the screen
        sendQuarterRow(pEpd, quarterLineBuffer);
        endSpiTransaction();
      }
    }
  }

  Debug::printProgMem(PSTR("Turning on display\r\n"));
  beginSpiTransaction();
  ret = pEpd->TurnOnDisplay();
  if(ret == FAILURE) {
    Debug::printProgMem(PSTR("TurnOnDisplay Failed\r\n"));
    Debug::error(ERRORCODE_EPAPER_FAILED_TURN_ON_DISPLAY);
  }
  endSpiTransaction();

display_image_cleanup:
  return ret;
}

void powerUpPeripherals() {
  Debug::printProgMem(PSTR("powerUpPeripherals\r\n"));

  // Set the SDCARD CS, SCLK and MOSI pins high so the SD CARD doesn't start 
  // reading the SPI bus when powered up
  pinMode(PIN_SD_CHIP_SELECT, OUTPUT);
  digitalWrite(PIN_SD_CHIP_SELECT, HIGH);

  pinMode(PIN_SCLK, OUTPUT);
  digitalWrite(PIN_SCLK, HIGH);
  
  pinMode(PIN_MOSI, OUTPUT);
  digitalWrite(PIN_MOSI, HIGH);

  // Turn on the peripheral power by setting power select low
  pinMode(PIN_POWER_SELECT, OUTPUT);
  digitalWrite(PIN_POWER_SELECT, LOW);

  delay(2);

  Debug::printProgMem(PSTR("-powerUpPeripherals\r\n"));
}

void powerDownPeripherals() {
  Debug::printProgMem(PSTR("powerDownPeripherals\r\n"));
  // Turn off the peripheral power by setting the power select GPIO high  
  digitalWrite(PIN_POWER_SELECT, HIGH);
  
  // If SCLK, MOSI or the CS lines are high, the SD Card board will draw power
  pinMode(PIN_SCLK, INPUT);
  pinMode(PIN_MOSI, INPUT);
  pinMode(PIN_SD_CHIP_SELECT, INPUT);
}

void beginSpiTransaction() {
  SPI.beginTransaction(SPISettings(8000000, MSBFIRST, SPI_MODE0));
}

void endSpiTransaction() {
  SPI.endTransaction();
}

void sendQuarterRow(Epd *pEpd, char *buffer) {
  for(int col = 0; col < EPD_WIDTH/8; col++) {
    // Convert 7-color to B/W - anything non-white becomes black
    uint8_t bwData = (buffer[col] == EPD_WHITE) ? 0xFF : 0x00;
    pEpd->SendData(bwData);
  }
}

int getNextFileHandle(SDFile &sdFile) {
  char filename[MAX_8_3_FILENAME_SIZE];

  Debug::printProgMem(PSTR("Get the next filename\r\n"));
  PictureIndex::getBmpFilename(filename);

  Debug::printProgMem(PSTR("Opening file "));
  Debug::print(filename);
  Debug::print("\r\n");
  sdFile = SD.open(filename, FILE_READ);
  if(sdFile) {
    Debug::printProgMem(PSTR("File opened.\r\n"));
    PictureIndex::incrementPictureIndex();
    EepromData::savePictureIndex();
    return SUCCESS;
  }

  if(PictureIndex::getPictureIndex()==0) {
    Debug::printProgMem(PSTR("Failed to open file pic_000.bmp.\r\n"));
    return FAILURE;
  } 

  Debug::printProgMem(PSTR("Failed to open file.\r\n"));
  sdFile.close();

  PictureIndex::clearPictureIndex();
  PictureIndex::updateInUsePictureIndex();
  PictureIndex::getBmpFilename(filename);

  Debug::printProgMem(PSTR("Opening file "));
  Debug::print(filename);
  Debug::printProgMem(PSTR("\r\n"));
  sdFile = SD.open(filename, FILE_READ);
  if(sdFile) {
    Debug::printProgMem(PSTR("File opened."));
    PictureIndex::incrementPictureIndex();
    EepromData::savePictureIndex();
    return SUCCESS;
  }

  Debug::printProgMem(PSTR("Failed to open any bmp file.\r\n"));
  return FAILURE;
}