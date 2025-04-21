# 🚂 Platform 1 Cafe

Hey there! I'm John, and over the recent years, I've been serving up coffee and smiles at Platform 1 Cafe, nestled right on Riversdale Station in beautiful Camberwell, Victoria. This little web app is my love letter to our cafe and our wonderful customers.

Check out the live site at [platform1cafe.com](https://platform1cafe.com) ☕

## 💭 The Story Behind This Project

Picture this: You're in the middle of a morning coffee rush, and the million dollar question I have on my mind is: "When's the next train?" For years, I'd have to stick my head out the cafe door to check the platform display. Not anymore! I built this web app to show real-time train departures right on your phone or computer. No more door-peeking needed! 😅

## ✨ Features

- **Live Train Times**: Real-time departures from Platform 1, straight from the PTV API
- **Clean Design**: Beautiful, easy-to-read interface that matches our cafe's cozy vibe
- **Always Updated**: Automatically refreshes to keep you on schedule
- **Mobile Friendly**: Check times on your phone while sipping your coffee ☕

## 🛠 Tech Stack

I went all-in on modern cloud tech for this project:
- **Frontend**: React app hosted on AWS Amplify (because we love smooth user experiences!)
- **Backend**: Serverless AWS Lambda functions (they're like our busy baristas - always ready to serve!)
- **Database**: DynamoDB (keeping our train times fresh and hot ☕)
- **Updates**: CloudWatch Events (our digital train spotter, never misses a beat)

## 🚀 Want to Run This Locally With Your Own PTV API?

### What You'll Need
- Node.js installed on your computer
- PTV API Credentials
- Environment variables set up (check `.env.example` for required values)

### Quick Start
1. Clone this slice of Platform 1:
   ```bash
   git clone https://github.com/your-username/platform1-cafe.git
   cd platform1-cafe
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   # IMPORTANT: Update the .env file with your values before proceeding!
   ```

3. Install:
   ```bash
   npm install
   ```

4. Fire it up:
   ```bash
   npm start
   ```

5. Visit `http://localhost:3000` and pretend you're at the cafe! 🎉

Or skip the setup and visit [platform1cafe.com](https://platform1cafe.com) to see it in action! 

## 🏗 Behind the Scenes

All the backend magic is documented in `backend/AWS_SETUP_GUIDE.md`. It's got everything you need to know about:
- Setting up the DynamoDB table (our digital timetable)
- Deploying Lambda functions (our cloud-based train spotters)
- Configuring API Gateway (the friendly conductor)
- Setting up CloudWatch Events (keeping everything running on time)

## 🔒 Safety First!

Just like we keep our coffee machine clean and maintained:
- All sensitive stuff (API keys, etc.) lives safely in AWS Lambda
- No secrets in the code
- Everything's properly secured with AWS IAM

## 💝 Special Thanks

A massive thank you to:
- Our amazing customers who make every day special
- The PTV for providing the API that makes this possible
- The wonderful community at Riversdale Station
- Everyone who's supported Platform 1 Cafe over the years

## Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure your environment variables in `.env`:
   - `REACT_APP_API_GATEWAY_URL`: Your AWS API Gateway endpoint
   - Add any other required environment variables

## Security Notes

- Never commit `.env` files containing real credentials
- All sensitive endpoints and keys are managed through environment variables
- AWS resources (Lambda, API Gateway, DynamoDB) should be configured through proper IAM roles and policies
- For local development, use placeholder values or development-specific endpoints

## Development Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

---
Made with 💕 by John | Platform 1 Cafe | Riversdale Station, Camberwell 
