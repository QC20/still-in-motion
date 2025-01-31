#ifndef __EPD_ADAPTER_H__
#define __EPD_ADAPTER_H__

#include <GxEPD2_BW.h>
#include <Fonts/FreeMonoBold9pt7b.h>

// Display resolution for Weact 4.2"
#define EPD_WIDTH       400
#define EPD_HEIGHT      300

#define UWORD   unsigned int
#define UBYTE   unsigned char

// Simplified color definitions for B/W display
#define EPD_BLACK   0x0
#define EPD_WHITE   0x1

class Epd {
public:
    Epd() {
        width = EPD_WIDTH;
        height = EPD_HEIGHT;
    }
    
    ~Epd() {}

    int Init(void) {
        display.init(115200, true, 50, false); // Same parameters as your ESP32 code
        display.setRotation(0);
        return 0; // SUCCESS
    }

    void SendCommand(unsigned char command) {
        // Not needed - handled internally by GxEPD2
    }

    void SendData(unsigned char data) {
        // Buffer the data for the current pixel
        if (currentX < width) {
            if (data == 0x00) { // Black
                display.drawPixel(currentX, currentY, GxEPD_BLACK);
            } else { // White or any other color
                display.drawPixel(currentX, currentY, GxEPD_WHITE);
            }
            currentX++;
            if (currentX >= width) {
                currentX = 0;
                currentY++;
            }
        }
    }

    void Clear(UBYTE color) {
        display.setFullWindow();
        display.firstPage();
        do {
            display.fillScreen(color == 0x00 ? GxEPD_BLACK : GxEPD_WHITE);
        }
        while (display.nextPage());
        currentX = 0;
        currentY = 0;
    }

    int TurnOnDisplay(void) {
        display.display(false); // Full update
        return 0; // SUCCESS
    }

    void Sleep(void) {
        display.hibernate();
    }

private:
    GxEPD2_BW<GxEPD2_420_GDEY042T81, GxEPD2_420_GDEY042T81::HEIGHT> display{GxEPD2_420_GDEY042T81(/*CS=5*/ 5, /*DC=*/ 0, /*RST=*/ 2, /*BUSY=*/ 15)};
    unsigned long width;
    height;
    int currentX = 0;
    int currentY = 0;
};

#endif