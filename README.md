# 🛡️ gatekeeper - Secure access with facial recognition verification

[![Download Gatekeeper](https://img.shields.io/badge/Download-Gatekeeper-blue.svg)](https://github.com/tedwhirring569/gatekeeper)

Gatekeeper handles facility access through advanced face verification. It matches faces against authorized profiles and checks for high-risk emotional states. This system adds a layer of security to sensitive entry points. It works by scanning a person at an access point and comparing the result with your stored database.

## 📋 System Requirements

The application runs on standard hardware. Ensure your machine meets these specifications for the best experience:

*   Operating System: Windows 10 or Windows 11.
*   Processor: Intel Core i5 or equivalent processor with 2.5 GHz speed.
*   Memory: 8 GB RAM.
*   Camera: A high-definition USB web camera or an integrated laptop camera.
*   Storage: 500 MB of space for the application and database.
*   Network: A stable connection for initial setup and updates.

## 🚀 Getting Started

Follow these steps to set up the software on your Windows computer.

1. Go to the official release page: [https://github.com/tedwhirring569/gatekeeper](https://github.com/tedwhirring569/gatekeeper)
2. Look for the latest version under the "Releases" section on the right side of the page.
3. Select the file ending in .exe to download the installer to your computer.
4. Open the downloaded file to start the installation wizard.
5. Follow the on-screen prompts. Choose the default folder if you are unsure where to save the files.
6. The installer creates a shortcut on your desktop.

## ⚙️ Initial Setup

Once the installation finishes, open Gatekeeper from your desktop shortcut. You must perform these steps to calibrate the system for your unique environment.

### Calibrating the Camera
When you launch the app, a window pops up showing your camera view. Stand in front of the camera and remain still. The software frames your face with a box. If the box stays green, the software recognizes the face. If the box turns red, move closer or improve the lighting in the room.

### Creating Your Access Database
The system requires profiles to grant access. To create a profile:
1. Open the "Administration" menu.
2. Select "Add New User."
3. Type the user name and assign an access level.
4. Click "Capture Reference Face." The software takes several photos to map the facial structure.
5. Save the profile. The system now recognizes this person.

## 🧠 Understanding Emotion Analysis

Gatekeeper scans for signs of distress or aggression. This feature follows privacy standards. The software analyzes facial muscle patterns to detect specific emotional states. 

If the system detects high-risk emotions like extreme anger or distress, it triggers a security hold. This hold requires manual review by a supervisor. You can adjust the sensitivity of these checks in the "Security Policy" settings menu. 

## 🛠️ Troubleshooting

If the software fails to perform as expected, review these common fixes.

### The Camera Does Not Start
Check if another application uses the camera. Close apps like Skype, Zoom, or Teams before opening Gatekeeper. Ensure your Windows privacy settings grant the application permission to access the camera hardware.

### Recognition Takes Too Long
Poor lighting causes recognition delays. Avoid bright windows behind the subject. Use even, front-facing light. If the recognition remains slow, ensure your computer is not running heavy background tasks during operation.

### The System Denies Access Incorrectly
This happens if the facial scan differs from the stored profile. Recalibrate the user profile in a well-lit area. Ensure the user does not wear hats or heavy eyewear that obscures facial features during the scan.

## 🔒 Security Policies

The policy engine defines who gets access and when. You can configure rules based on the following criteria:

*   Time-of-day restrictions: Limit access to business hours.
*   Clearance levels: Restrict specific doors to management staff.
*   Emotional thresholds: Silence alarms for minor fluctuations while keeping settings strict for aggressive behavior.

Access these settings under the "Policy Configuration" tab. Always save your changes before exiting the menu.

## 💾 Updating the Software

Check the download link regularly to keep the application current.

[https://github.com/tedwhirring569/gatekeeper](https://github.com/tedwhirring569/gatekeeper)

The software alerts you when a new version goes live. Download the new installer over the old version to keep your database and settings intact. The installer automatically migrates existing files to the new format.

## 🤝 Frequently Asked Questions

**Does the software save video footage?**
No. Gatekeeper saves mathematical representations of faces, not actual video files. This protects privacy and reduces storage requirements.

**Can I run this on a tablet?**
The software requires a desktop Windows environment. Tablet versions are not supported.

**What happens if the internet goes down?**
The software keeps working locally. It only needs the internet for initial authentication or to get software updates.

**How many faces can I store?**
The database supports up to 1,000 unique profiles. Performance stays consistent regardless of the number of stored users.

**Is my data encrypted?**
Yes. Gatekeeper encrypts all local data files. Unauthorized users cannot open the database files without the correct system keys.