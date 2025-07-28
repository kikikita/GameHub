import { useState } from "react";
import styles from "./VisualNovel.module.css";

interface Choice {
  id: string;
  text: string;
  action: () => void;
}

interface Scene {
  id: string;
  backgroundImage: string;
  text: string;
  choices: Choice[];
}

// Sample scenes for demonstration
const sampleScenes: Scene[] = [
  {
    id: "scene1",
    backgroundImage:
      "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
    text: "You find yourself standing at the edge of a mystical forest. The ancient trees seem to whisper secrets in the wind, and two paths stretch before you, disappearing into the shadows.",
    choices: [
      {
        id: "choice1",
        text: "Take the left path through the dark woods",
        action: () => console.log("Taking left path"),
      },
      {
        id: "choice2",
        text: "Take the right path along the moonlit stream",
        action: () => console.log("Taking right path"),
      },
    ],
  },
  {
    id: "scene2",
    backgroundImage:
      "https://images.unsplash.com/photo-1518837695005-2083093ee35b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
    text: "You arrive at an ancient library filled with floating books and glowing crystals. A mysterious figure in robes approaches you with an important question.",
    choices: [
      {
        id: "choice1",
        text: "Ask about the floating books",
        action: () => console.log("Asking about books"),
      },
      {
        id: "choice2",
        text: "Inquire about the glowing crystals",
        action: () => console.log("Asking about crystals"),
      },
    ],
  },
];

function VisualNovel() {
  const [currentSceneIndex, setCurrentSceneIndex] = useState(0);
  const [isUIVisible, setIsUIVisible] = useState(true);

  const currentScene = sampleScenes[currentSceneIndex];

  const handleChoice = (choice: Choice) => {
    // Execute choice action
    choice.action();

    // Move to next scene
    setCurrentSceneIndex((prev) => (prev + 1) % sampleScenes.length);
  };

  const toggleUI = () => {
    setIsUIVisible(!isUIVisible);
  };

  return (
    <div className={styles.visualNovel}>
      <div
        className={styles.background}
        style={{ backgroundImage: `url(${currentScene.backgroundImage})` }}
      />
      {!isUIVisible && (
        <button
          className={styles.showUIButton}
          onClick={toggleUI}
          aria-label="Show UI"
        >
          <svg
            width="12"
            height="8"
            viewBox="0 0 24 24"
            fill="none"
            className={styles.arrowIcon}
          >
            <path
              d="M18 15l-6-6-6 6"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      )}

      {/* Main UI with sliding animation */}
      <div
        className={`${styles.ui} ${
          isUIVisible ? styles.uiVisible : styles.uiHidden
        }`}
      >
        {/* Hide UI button above text */}
        <button
          className={styles.hideUIButton}
          onClick={toggleUI}
          aria-label="Hide UI"
        >
          <svg
            width="12"
            height="8"
            viewBox="0 0 24 24"
            fill="none"
            className={styles.arrowIcon}
          >
            <path
              d="M6 9l6 6 6-6"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <div className={styles.textContainer}>
          <div className={styles.text}>{currentScene.text}</div>
        </div>

        <div className={styles.choices}>
          {currentScene.choices.map((choice) => (
            <button
              key={choice.id}
              className={styles.choiceButton}
              onClick={() => handleChoice(choice)}
            >
              {choice.text}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default VisualNovel;
