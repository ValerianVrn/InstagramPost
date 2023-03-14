import Head from "next/head";
import { useState } from "react";
import styles from "./index.module.css";
import Banner from './components/Banner.js';
import Facebook from './Facebook';
import LoadingButton from './components/LoadingButton.js';

export default function InstagramPost() {
  // Image description generation
  const [systemPrompt, setSystemPrompt] = useState("You are a charming Instagramer who posts pastries in nice backgrounds with a touch of humor.");
  const [userPrompt1, setUserPrompt1] = useState("Create an Instagram post of an apple pie with a ice cream on sunset. This is the first post of the account.");
  const [assistantPrompt, setAssistantPrompt] = useState("Welcome to my dessert adventure! 🍨🍎 As my first post, I'm sharing my all-time favorite dessert - warm apple pie with a scoop of vanilla ice cream, enjoyed during a beautiful sunset. There's something magical about the combination of sweet and tart flavors with a creamy finish. Who's ready for a slice? 🤤 #applepie #vanillaicecream #sunsetdessert #sweettoothsatisfied #dessertadventure #firstpost");
  const [userPrompt2, setUserPrompt2] = useState("Just answer what would be the best input for DALL-E to describe a pastry in a nice background in Savoie in winter.");
  const [isImageDescriptionLoading, setImageDescriptionIsLoading] = useState(false);
  // Image generation generation
  const [imageGenerationInput, setImageGenerationInput] = useState("");
  const [isImageGenerationLoading, setImageGenerationIsLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  // Caption
  const [userPrompt3, setUserPrompt3] = useState("This is the last day in Savoie. Generate a caption with a sense of humour, joy and famous hashtags.");
  const [isCaptionLoading, setIsCaptionLoading] = useState(false);
  const [caption, setCaption] = useState('');
  // Instagram post
  const { loginAndPublish } = Facebook();
  const [isPostLoading, setIsPostLoading] = useState(false);

  async function handleSubmitImageDescriptionInput(event) {
    event.preventDefault();
    setImageDescriptionIsLoading(true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          messages: [
            {role: "system", content: systemPrompt},
            {role: "user", content: userPrompt1},
            {role: "assistant", content: assistantPrompt},
            {role: "user", content: userPrompt2},
        ] 
        }),
      });

      const data = await response.json();
      if (response.status !== 200) {
        throw data.error || new Error(`Request failed with status ${response.status}`);
      }
      setImageGenerationInput(data.result);
    } catch(error) {
      console.error(error);
      alert(error.message);
    }  
    setImageDescriptionIsLoading(false);
  }

  async function handleSubmitImageGenerationInput(event) {
    event.preventDefault();
    setImageGenerationIsLoading(true);
    try {
      const response = await fetch("/api/image", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ description: imageGenerationInput }),
      });

      const data = await response.json();
      if (response.status !== 200) {
        throw data.error || new Error(`Request failed with status ${response.status}`);
      }

      setImageUrl(data.result);
    } catch(error) {
      console.error(error);
      alert(error.message);
    }
    setImageGenerationIsLoading(false);
  }

  async function handleSubmitCaption(event) {
    event.preventDefault();
    setIsCaptionLoading(true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          messages: [
            {role: "system", content: systemPrompt},
            {role: "user", content: userPrompt1},
            {role: "assistant", content: assistantPrompt},
            {role: "user", content: userPrompt2},
            {role: "assistant", content: imageGenerationInput},
            {role: "user", content: userPrompt3},
          ] 
        }),
      });

      const data = await response.json();
      if (response.status !== 200) {
        throw data.error || new Error(`Request failed with status ${response.status}`);
      }

      setCaption(data.result);
    } catch(error) {
      console.error(error);
      alert(error.message);
    }
    setIsCaptionLoading(false);
  }

  async function handleSubmitPost(event) {
    event.preventDefault();
    setIsPostLoading(true);
    try {
      loginAndPublish(imageUrl, caption);
      alert("Posted!");
    } catch(error) {
      console.error(error);
      alert(error.message);
    }
    setIsPostLoading(false);
  }

  function handleSystemPromptChange(event) {
    setSystemPrompt(event.target.value);
  }

  function handleUserPrompt1Change(event) {
    setUserPrompt1(event.target.value);
  }

  function handleAssistantPromptChange(event) {
    setAssistantPrompt(event.target.value);
  }

  function handleUserPrompt2Change(event) {
    setUserPrompt2(event.target.value);
  }

  function handleImageGenerationInputChange(event) {
    setImageGenerationInput(event.target.value);
  }

  function handleUserPrompt3Change(event) {
    setUserPrompt3(event.target.value);
  }

  function handleCaptionChange(event) {
    setCaption(event.target.value);
  }

  return (
    <div>
      <Head>
        <title>Instagram post with ChatGPT</title>
        <link rel="icon" href="/image.png" />
      </Head>
      <Banner />
      <main className={styles.main}>
        <div style={{ display: 'flex', width: 'auto', height:'auto' }}>
          <div className={styles.column}>            
            <h3>Tuning</h3>
            <label htmlFor="systemPrompt">IA profile</label>
            <textarea id="systemPrompt" type="text" value={systemPrompt} onChange={handleSystemPromptChange} />
            <label htmlFor="userPrompt1">User question</label>
            <textarea id="userPrompt1" type="text" value={userPrompt1} onChange={handleUserPrompt1Change} />
            <label htmlFor="assistantPrompt">IA answer</label>
            <textarea id="assistantPrompt" type="text" value={assistantPrompt} onChange={handleAssistantPromptChange} />
          </div>
          <div className={styles.column}>
            <h3>Topic</h3>
            <form onSubmit={handleSubmitImageDescriptionInput}>
              <label htmlFor="userPrompt2">Instructions</label>
              <textarea id="userPrompt2" type="text" value={userPrompt2} onChange={handleUserPrompt2Change} />
              <LoadingButton isLoading={isImageDescriptionLoading} type="submit">Generate image description</LoadingButton>
            </form>
          </div>
          <div className={styles.column}>
            <h3>Image</h3>
            <form onSubmit={handleSubmitImageGenerationInput}>
              <label htmlFor="imageGenerationInput">Image generation input</label>
              <textarea id="imageGenerationInput" type="text" value={imageGenerationInput} onChange={handleImageGenerationInputChange} />
              <LoadingButton isLoading={isImageGenerationLoading} type="submit">Generate image</LoadingButton>
            </form>
          </div>
          <div className={styles.column}>
            <h3>Caption</h3>
            <form onSubmit={handleSubmitCaption}>
              <label htmlFor="userPrompt3">Caption input</label>
              <textarea id="userPrompt3" type="text" value={userPrompt3} onChange={handleUserPrompt3Change} />
              <LoadingButton isLoading={isCaptionLoading} type="submit">Generate caption</LoadingButton>
            </form>
          </div>
          <div className={styles.column}>
            <h1>Preview</h1>
            <label htmlFor="imageUrl">Image URL</label>
            <input type="text" value={imageUrl}  onChange={(event) => setImageUrl(event.target.value)} />
            <img src={imageUrl} alt="Generated Image" />
            <textarea id="caption" type="text" value={caption} onChange={handleCaptionChange} />
            <form onSubmit={handleSubmitPost}>
              <LoadingButton isLoading={isPostLoading} type="submit">Post</LoadingButton>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
