# Still in Motion

Still in Motion is an artistic project that transforms the cinematic experience into a meditative display on a static e-paper screen. For this rendition, we feature the 2015 masterpiece Embrace of the Serpent.

The idea is straightforward yet deeply impactful: the entire film is presented frame by frame, with each frame displayed for 24 minutes. This creates a "faux frame rate" of 24 frames per hour, turning the traditionally fleeting nature of film into a slow and contemplative journey. At this pace, the 125-minute runtime of Embrace of the Serpent extends to an immersive experience lasting approximately 125 days.

This project invites viewers to engage with film in a new way—one that blurs the lines between motion and stillness, storytelling and reflection.

## **How to Use**

1. Insert an SD card loaded with compatible images (BMP format, 400x300 resolution).
2. Turn on the frame by inserting batteries or connecting a power source.
3. Press the button to cycle through images at your leisure.

### **Single Button Functionality**

The picture frame is controlled by a single button, providing a simple and intuitive way to interact with the device.

1. **Starting Image Display:**
   - Pressing the button initiates the image display cycle. 
   - Images are displayed one after another at a set interval until the frame enters sleep mode.

2. **Skipping to the Next Image:**
   - If you press the button while the frame is displaying images, it will immediately skip to the next image in the series.
   - This is useful for manually advancing or if an error occurs with the current image.

3. **Memory of Current Position:**
   - The frame tracks its position in the image sequence using EEPROM. 
   - When you press the button to skip to the next image, the EEPROM counter increments, ensuring that the next cycle resumes from the correct position.

---

## Things used for this project

- Frame with dimensions 85 mm × 64 mm (display measurements) 
- WeAct 4.2'' 4.2 Inch Epaper Module (link)[https://www.aliexpress.com/item/1005007133350270.html?spm=a2g0o.detail.pcDetailTopMoreOtherSeller.2.294e41nz41nzrb&gps-id=pcDetailTopMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=fdf973a0-43ec-4137-b5b9-302a5b209ea0&_t=gps-id:pcDetailTopMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:fdf973a0-43ec-4137-b5b9-302a5b209ea0,tpp_buckets:668%232846%238109%231935&pdp_npi=4%40dis%21USD%2123.37%2121.70%21%21%21169.33%21157.23%21%40211b431017377138436145030e382c%2112000039517565965%21rec%21DK%212622682955%21X&utparam-url=scene%3ApcDetailTopMoreOtherSeller%7Cquery_from%3A]
- Battery





# Battery Life and Power Consumption

It takes about 10 seconds to change the image on the screen. During this time, it uses approximately 40mA.

\[
= 10 \, \text{(seconds/switch)} \times 40 \, \text{(mA)} / 3600 \, \text{(seconds/hour)}
= 0.111 \, \text{(mAh/switch)}
\]

When idle, the current draw is about 10 µA.

\[
= 10 \, \text{(minutes)} \times 0.01 \, \text{(mA)} / 60 \, \text{(minutes/hour)}
= 0.017 \, \text{(mAh)}
\]

An approximate alkaline AAA battery life is about 1200mAh. However, the picture frame cannot use the full capacity of the battery. Once the voltage goes below 3.8V (1.25V per cell), the picture frame will stop working. This is about 50% of the capacity.

Therefore, the battery life for the picture frame is:

\[
= 1200 \, \text{(mAh)} \times 0.5
= 600 \, \text{(mAh)} / 0.128 \, \text{(mAh/cycle)}
= 4687 \, \text{(cycles)}
\]

\[
= 936 \, \text{(days)}
\]

\[
\approx 2.56 \, \text{(years)}
\]
