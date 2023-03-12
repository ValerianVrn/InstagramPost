# Startup

It requires a HTTPS connexion. Use ngrok with the command:
ngrok http 3000 --region us
The US region is required otherwise Facebook would detect the URL as malicious or abusive.

Go to the Facebook login for Business app from the Meta for developers page of GourmetPastryTransformer: https://developers.facebook.com/apps/596915082341166/business-login/settings/.
Copy the URL created with ngrok in "URI de redirection OAuth valides". Under "Paramètres OAuth client"

# OpenAI API Quickstart - Node.js example app

This is an example pet name generator app used in the OpenAI API [quickstart tutorial](https://platform.openai.com/docs/quickstart). It uses the [Next.js](https://nextjs.org/) framework with [React](https://reactjs.org/). Check out the tutorial or follow the instructions below to get set up.

![Text box that says name my pet with an icon of a dog](https://user-images.githubusercontent.com/10623307/213887080-b2bc4645-7fdb-4dbd-ae42-efce00d0dc29.png)


## Setup

1. If you don’t have Node.js installed, [install it from here](https://nodejs.org/en/) (Node.js version >= 14.6.0 required)

2. Clone this repository

3. Navigate into the project directory

   ```bash
   $ cd openai-quickstart-node
   ```

4. Install the requirements

   ```bash
   $ npm install
   ```

5. Make a copy of the example environment variables file

   On Linux systems: 
   ```bash
   $ cp .env.example .env
   ```
   On Windows:
   ```powershell
   $ copy .env.example .env
   ```
6. Add your [API key](https://platform.openai.com/account/api-keys) to the newly created `.env` file

7. Run the app

   ```bash
   $ npm run dev
   ```

You should now be able to access the app at [http://localhost:3000](http://localhost:3000)! For the full context behind this example app, check out the [tutorial](https://platform.openai.com/docs/quickstart).
