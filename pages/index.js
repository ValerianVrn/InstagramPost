import Head from "next/head";
import { useEffect, useState } from "react";
import styles from "./index.module.css";
import Facebook from './Facebook';
import { useAuth } from './components/AuthContext';
import { useRouter } from 'next/router';
import { Accordion, Button, Card, Container, Nav, Navbar, NavDropdown, Spinner } from 'react-bootstrap';

const GOURMETPASTRYTRANSFORMER = {
  name: "Gourmet Pastry Transformer",
  facebookAppId: process.env.GOURMETPASTRYTRANSFORMER_FACEBOOK_APP_ID,
  systemPrompt: "You are a charming Instagramer who posts pastries in nice backgrounds with a touch of humor.",
  userPrompt1: "Create an Instagram post of an apple pie with a ice cream on sunset. This is the first post of the account.",
  assistantPrompt: "Welcome to my dessert adventure! 🍨🍎 As my first post, I'm sharing my all-time favorite dessert - warm apple pie with a scoop of vanilla ice cream, enjoyed during a beautiful sunset. There's something magical about the combination of sweet and tart flavors with a creamy finish. Who's ready for a slice? 🤤 #applepie #vanillaicecream #sunsetdessert #sweettoothsatisfied #dessertadventure #firstpost",
  userPrompt2: "Give an accurate and factual description of a photo with a pastry in the foreground and a nice view from Savoie in winter in the background. Keep it simple and focus on the elements of the scene.",
  userPrompt3: "This is the last day in Savoie. Generate a hilarious caption with famous hashtags."
};

const GENIUSPETTALES = {
  name: "Genius Pet Tales",
  facebookAppId: process.env.GENIUSPETTALES_FACEBOOK_APP_ID,
  systemPrompt: "You are an Instagramer who showcases cute animals in unique and creative settings and situations! To differentiate your profile, you add a narrative element to your images, creating a storyline or adventure for each animal. You always use famous hashtags.",
  userPrompt1: "Create a post (image description and caption).",
  assistantPrompt: "Image description: a fluffy white cat with big blue eyes stands at the edge of a cliff, gazing out at a breathtakingly beautiful world of floating islands, crystal-clear waterfalls, and colorful clouds. The cat looks ready to embark on an exciting adventure.\nCaption: Meet Luna, our brave explorer cat! She's always up for an adventure, and today she's discovered a magical world full of wonder and excitement. Luna can't wait to explore every corner of this fantastical land and see what mysteries await her. Do you have any suggestions for where Luna should go next? Let us know in the comments! #CuteAnimals #PetsofInstagram #CreativeInspiration #ExploreMore #ImaginaryWorlds",
  userPrompt2: "Find a topic for today and give the image description.",
  userPrompt3: "Create the caption."
};

function InstagramPost() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [sdkInitialized, setSdkInitialized] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
    // initFacebook();
  }, [isAuthenticated]);

  // Account
  const [currentAccount, setCurrentAccount] = useState(GOURMETPASTRYTRANSFORMER);

  // Image description generation
  const [systemPrompt, setSystemPrompt] = useState(GOURMETPASTRYTRANSFORMER.systemPrompt);
  const [userPrompt1, setUserPrompt1] = useState(GOURMETPASTRYTRANSFORMER.userPrompt1);
  const [assistantPrompt, setAssistantPrompt] = useState(GOURMETPASTRYTRANSFORMER.assistantPrompt);
  const [userPrompt2, setUserPrompt2] = useState(GOURMETPASTRYTRANSFORMER.userPrompt2);
  const [isImageDescriptionLoading, setImageDescriptionIsLoading] = useState(false);
  // Image generation generation
  const [imageGenerationInput, setImageGenerationInput] = useState("");
  const [isImageGenerationLoading, setImageGenerationIsLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  // Caption
  const [userPrompt3, setUserPrompt3] = useState(GOURMETPASTRYTRANSFORMER.userPrompt3);
  const [isCaptionLoading, setIsCaptionLoading] = useState(false);
  const [caption, setCaption] = useState('');
  // Instagram post
  // const { loginAndPublish } = Facebook();
  const [isPostLoading, setIsPostLoading] = useState(false);

  function initFacebook() {
    
    // Initialize Facebook SDK.
    window.fbAsyncInit = () => {
      FB.init({
        appId: currentAccount.facebookAppId,
        cookie: true,
        xfbml: true,
        version: 'v16.0'
      })};

      // Set the initialization status to true.
      setSdkInitialized(true);
  }

  async function handleChangeAccount(eventKey) {
    if (eventKey === GOURMETPASTRYTRANSFORMER.name) {
      setCurrentAccount(GOURMETPASTRYTRANSFORMER);
    }
    else if (eventKey === GENIUSPETTALES.name) {
      setCurrentAccount(GENIUSPETTALES);
    }
    initFacebook();
    setSystemPrompt(currentAccount.systemPrompt);
    setUserPrompt1(currentAccount.userPrompt1);
    setAssistantPrompt(currentAccount.assistantPrompt);
    setUserPrompt2(currentAccount.userPrompt2);
    setUserPrompt3(currentAccount.userPrompt3);
  }

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
      initFacebook();
      const { loginAndPublish } = Facebook();

      loginAndPublish(imageUrl, caption);
      alert("Posted!");
    } catch(error) {
      console.error(error);
      alert(error.message);
    }
    setIsPostLoading(false);
  }

  return (
    <div>
      <Head>
        <title>Instagram post with ChatGPT</title>
        <link rel="icon" href="/image.png" />
      </Head>
      <Navbar bg="dark" variant="dark" className="mb-3" onSelect={handleChangeAccount}>
        <Container>
          <Navbar.Brand href="/">
            <img alt="" src="/image.png" width="30" height="30" className="d-inline-block align-top" />{' '}
            Instagram post with ChatGPT
          </Navbar.Brand>
          <Nav className="me-auto">
            <NavDropdown title={currentAccount.name} id="basic-nav-dropdown">
              <NavDropdown.Item eventKey={GOURMETPASTRYTRANSFORMER.name}>{GOURMETPASTRYTRANSFORMER.name}</NavDropdown.Item>
              <NavDropdown.Item eventKey={GENIUSPETTALES.name}>{GENIUSPETTALES.name}</NavDropdown.Item>
            </NavDropdown>
          </Nav>
        </Container>
      </Navbar>
      <main className="mb-3">
        <Accordion defaultActiveKey={['1', '2', '3']} alwaysOpen className="container-lg">
          <Accordion.Item eventKey="0">
            <Accordion.Header>Tuning</Accordion.Header>
            <Accordion.Body>
              <div className="mb-3">
                <label htmlFor="systemPrompt" className="form-label">IA profile</label>
                <textarea id="systemPrompt" className="form-control" type="text" rows="4" value={systemPrompt} onChange={(event) => setSystemPrompt(event.target.value)} />
              </div>
              <div className="mb-3">
                <label htmlFor="userPrompt1" className="form-label">User question</label>
                <textarea id="userPrompt1" className="form-control" type="text" rows="4" value={userPrompt1} onChange={(event) => setUserPrompt1(event.target.value)} />
              </div>
              <div className="mb-3">
                <label htmlFor="assistantPrompt" className="form-label">IA answer</label>
                <textarea id="assistantPrompt" className="form-control" type="text" rows="10" value={assistantPrompt} onChange={(event) => setAssistantPrompt(event.target.value)} />
              </div>
            </Accordion.Body>
          </Accordion.Item>
          <Accordion.Item eventKey="1">
            <Accordion.Header>Topic</Accordion.Header>
            <Accordion.Body>
              <form onSubmit={handleSubmitImageDescriptionInput}>
                <div className="mb-3">
                  <label htmlFor="userPrompt2" className="form-label">Instructions</label>
                  <textarea id="userPrompt2" className="form-control" type="text" rows="4" value={userPrompt2} onChange={(event) => setUserPrompt2(event.target.value)} />
                </div>
                <Button variant="primary" disabled={isImageDescriptionLoading} type="submit">
                {!isImageDescriptionLoading ? 'Generate image description':
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />}
                </Button>
              </form>
            </Accordion.Body>
          </Accordion.Item>
          <Accordion.Item eventKey="2">
            <Accordion.Header>Image</Accordion.Header>
            <Accordion.Body>
              <form onSubmit={handleSubmitImageGenerationInput}>
                <div className="mb-3">
                  <label htmlFor="imageGenerationInput" className="form-label">Image generation input</label>
                  <textarea id="imageGenerationInput" className="form-control" type="text" rows="4" value={imageGenerationInput} onChange={(event) => setImageGenerationInput(event.target.value)} />
                </div>
                <Button variant="primary" disabled={isImageDescriptionLoading} type="submit">
                {!isImageGenerationLoading ? 'Generate image':
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />}
                </Button>
              </form>
            </Accordion.Body>
          </Accordion.Item>
          <Accordion.Item eventKey="3">
            <Accordion.Header>Caption</Accordion.Header>
            <Accordion.Body>
              <form onSubmit={handleSubmitCaption}>
                <div className="mb-3">
                  <label htmlFor="userPrompt3" className="form-label">Caption input</label>
                  <textarea id="userPrompt3" className="form-control" type="text" rows="4" value={userPrompt3} onChange={(event) => setUserPrompt3(event.target.value)} />
                </div>
                <Button variant="primary" disabled={isCaptionLoading} type="submit">
                {!isCaptionLoading ? 'Generate caption':
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />}
                </Button>
              </form>
            </Accordion.Body>
          </Accordion.Item>
        { !sdkInitialized ? (
          <div className="d-flex m-3 justify-content-center">
            <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
            <label> Loading Facebook app...</label>
          </div>
          ) : (
          <Card>
            <Card.Header>Preview</Card.Header>
            <Card.Img variant="top" src={imageUrl}></Card.Img>
            <Card.Body>
              <div className="mb-3">
                <label htmlFor="imageUrl" className="form-label">Image URL</label>
                <input type="text" className="form-control" value={imageUrl} onChange={(event) => setImageUrl(event.target.value)} />
              </div>
              <Card.Text>
                <div className="mb-3">
                  <textarea id="caption" className="form-control" type="text" rows="10" value={caption} onChange={(event) => setCaption(event.target.value)} />
                </div>
                <form onSubmit={handleSubmitPost}>
                  <Button variant="success" disabled={isPostLoading} type="submit">
                  {!isPostLoading ? 'Post':
                    <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />}
                  </Button>
                </form>
              </Card.Text>
            </Card.Body>
          </Card>
          )}
        </Accordion>
      </main>
    </div>
  );
}

export default InstagramPost;