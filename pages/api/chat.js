import { Configuration, OpenAIApi } from "openai";

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

export default async function (req, res) {
  if (!configuration.apiKey) {
    res.status(500).json({
      error: {
        message: "OpenAI API key not configured, please follow instructions in README.md",
      }
    });
    return;
  }

  const messages = req.body.messages || '';
  if (messages.length === 0) {
    res.status(400).json({
      error: {
        message: "Please enter valid messages",
      }
    });
    return;
  }

  try {
    const completion = await openai.createChatCompletion({
      model: "gpt-3.5-turbo",
      messages: messages,
      temperature: 0.6,
    });
    console.log(completion.data.choices[0].message);
    res.status(200).json({ result: completion.data.choices[0].message.content });
  } catch(error) {
    // Consider adjusting the error handling logic for your use case
    if (error.response) {
      console.error(error.response.status, error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      console.error(`Error with OpenAI API request: ${error.message}`);
      res.status(500).json({
        error: {
          message: 'An error occurred during your request.',
        }
      });
    }
  }
}

function generatePrompt(animal) {
  const capitalizedAnimal =
    animal[0].toUpperCase() + animal.slice(1).toLowerCase();
  return [
    {role: "system", content: "You are a charming Instagramer who posts pastries in nice backgrounds. You have a sense of humour and you are joyful. You use famous hashtags."},
    {role: "user", content: "Create an Instagram post of an apple pie with a ice cream on sunset. This is the first post of the account."},
    {role: "assistant", content: "Welcome to my dessert adventure! 🍨🍎 As my first post, I'm sharing my all-time favorite dessert - warm apple pie with a scoop of vanilla ice cream, enjoyed during a beautiful sunset. There's something magical about the combination of sweet and tart flavors with a creamy finish. Who's ready for a slice? 🤤 #applepie #vanillaicecream #sunsetdessert #sweettoothsatisfied #dessertadventure #firstpost"},
    {role: "user", content: "Generate an Instagram post of chocolate macarons and champagne at Courchevel. Highlight the macaron love and simple pleasure."},
    {role: "assistant", content: "Life is short, but sweet moments like these are forever. 🍫🥂 There's nothing like indulging in the simple pleasure of biting into a perfectly crafted chocolate macaron, while sipping on a glass of champagne in the heart of Courchevel. ❄️☃️ #macaronlove #sweetmoment #champagnelife #courchevel #indulgence #simplepleasures"},
    {role: "user", content: `Generate a post about ${capitalizedAnimal}.`}
];
}
