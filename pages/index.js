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
  const [isImageDescriptionDebug, setImageDescriptionIsDebug] = useState(false);
  const [imageDescriptionDebug, setImageDescriptionDebug] = useState('');
  const [isImageDescriptionLoading, setImageDescriptionIsLoading] = useState(false);
  const [imageDescription, setImageDescription] = useState('');
  // Image generation generation
  const [imageGenerationInput, setImageGenerationInput] = useState("");
  const [isImageGenerationLoading, setImageGenerationIsLoading] = useState(false);
  const [isImageDebug, setImageDebug] = useState(false);
  const [imageUrlDebug, setImageUrlDebug] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  // Caption
  const [userPrompt3, setUserPrompt3] = useState("This is the last day in Savoie. Generate a caption with a sense of humour, joy and famous hashtags.");
  const [isCaptionLoading, setIsCaptionLoading] = useState(false);
  const [isCaptionDebug, setIsCaptionDebug] = useState(false);
  const [captionDebug, setCaptionDebug] = useState('');
  const [caption, setCaption] = useState('');
  // Instagram post
  const { loginAndPublish } = Facebook();
  const [isPostLoading, setIsPostLoading] = useState(false);
  const [isPostDebug, setIsPostDebug] = useState(false);

  async function handleSubmitImageDescriptionInput(event) {
    event.preventDefault();
    setImageDescriptionIsLoading(true);
    try {
      let data;
      if (!isImageDescriptionDebug) {
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

        data = await response.json();
        if (response.status !== 200) {
          throw data.error || new Error(`Request failed with status ${response.status}`);
        }
      }
      else {
        await new Promise(resolve => setTimeout(resolve, 1000));
        data = { result: imageDescriptionDebug};
      }
      setImageDescription(data.result);
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
      let data;
      if (!isImageDebug) {
        const response = await fetch("/api/image", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ description: imageGenerationInput }),
        });

        data = await response.json();
        if (response.status !== 200) {
          throw data.error || new Error(`Request failed with status ${response.status}`);
        }
      }
      else {
        await new Promise(resolve => setTimeout(resolve, 1000));
        data = { result: imageUrlDebug};
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
      let data;
      if (!isCaptionDebug) {
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

        data = await response.json();
        if (response.status !== 200) {
          throw data.error || new Error(`Request failed with status ${response.status}`);
        }
      }
      else {
        await new Promise(resolve => setTimeout(resolve, 1000));
        data = { result: captionDebug};
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
      if (!isPostDebug) {
        loginAndPublish(imageUrl, caption);
      }
      else {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

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
              <label>
                <input type="checkbox" checked={isImageDescriptionDebug} onChange={() => setImageDescriptionIsDebug(!isImageDescriptionDebug)} /> 
                Debug
              </label>
              {isImageDescriptionDebug && (
                <textarea id="imageDescriptionDebug" type="text" value={imageDescriptionDebug} onChange={(event) => setImageDescriptionDebug(event.target.value)} />
              )}
            </form>
          </div>
          {imageDescription && (
          <div className={styles.column}>
            <h3>Image</h3>
            <form onSubmit={handleSubmitImageGenerationInput}>
              <label htmlFor="imageGenerationInput">Image generation input</label>
              <textarea id="imageGenerationInput" type="text" value={imageGenerationInput} onChange={handleImageGenerationInputChange} />
              <LoadingButton isLoading={isImageGenerationLoading} type="submit">Generate image</LoadingButton>
              <label>
                <input type="checkbox" checked={isImageDebug} onChange={() => setImageDebug(!isImageDebug)} /> 
                Debug
              </label>
              {isImageDebug && (
                <textarea id="isImageDebug" type="text" value={imageUrlDebug} onChange={(event) => setImageUrlDebug(event.target.value)} />
              )}
            </form>
          </div>
          )}
          {imageUrl && (
          <div className={styles.column}>
            <h3>Caption</h3>
            <input type="text" value={imageUrl}  onChange={(event) => setImageUrl(event.target.value)} />
            <img src={imageUrl} alt="Generated image" />
            <form onSubmit={handleSubmitCaption}>
              <label htmlFor="userPrompt3">Caption input</label>
              <textarea id="userPrompt3" type="text" value={userPrompt3} onChange={handleUserPrompt3Change} />
              <LoadingButton isLoading={isCaptionLoading} type="submit">Generate caption</LoadingButton>
              <label>
                <input type="checkbox" checked={isCaptionDebug} onChange={() => setIsCaptionDebug(!isCaptionDebug)} /> 
                Debug
              </label>
              {isCaptionDebug && (
                <textarea id="captionDebug" type="text" value={captionDebug} onChange={(event) => setCaptionDebug(event.target.value)} />
              )}
            </form>
          </div>
          )}
          {caption && (
          <div className={styles.column}>
            <h1>Preview</h1>
            <img src={imageUrl} alt="Generated Image" />
            <textarea id="caption" type="text" value={caption} onChange={handleCaptionChange} />
            <form onSubmit={handleSubmitPost}>
              <LoadingButton isLoading={isPostLoading} type="submit">Post</LoadingButton>
              <label>
                <input type="checkbox" checked={isPostDebug} onChange={() => setIsPostDebug(!isPostDebug)} /> 
                Debug
              </label>
            </form>
          </div>
          )}
        </div>
      </main>
    </div>
  );
}
