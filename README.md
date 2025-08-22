[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=30&pause=1000&color=87CEEB&center=true&vCenter=true&width=850&lines=🎮+Temperature+Control:+Hypnotic+Edition!+❄️🔥)](https://git.io/typing-svg)

Welcome to **Temperature Control: Hypnotic Edition\!** This is a fast-paced, addictive arcade-style game built with Python and Pygame. Take control of a powerful Air Conditioning unit, navigate a hypnotic vortex, collect fans for points, and dodge the relentless onslaught of sentient heaters\! 🌀

This project also features optional **Web3 integration** 🔗, allowing players to submit their high scores to an Ethereum-based blockchain.

-----

## ✨ Features

  - **🚀 Endless Arcade Action:** The challenge never stops\! Heaters spawn faster and move quicker as your score increases.
  - **🎨 Hypnotic Visuals:** A mesmerizing, rotating vortex background with particle effects and smooth animations.
  - **⚡ Power-ups:** Collect special items like a **Shield**, a **Score Booster**, or an extra **Life** to extend your run.
  - **💥 Special Ability:** Use the "Blast" ability to temporarily freeze all heaters on screen, giving you a chance to escape a tight spot.
  - **🏆 Local High Score:** The game saves your highest score locally in a `highscore.txt` file.
  - **💎 Optional Web3 Integration:** Connect to an Ethereum network to submit your new high scores on-chain\!

-----

## 🕹️ Gameplay & Controls

### 🎯 Objective

The goal is simple: **survive for as long as you can and get the highest score possible.**

  - You control the **AC unit** (your player).
  - You must avoid the red **Heaters** that chase you around the screen. Colliding with one will cost you a life.
  - Collect the spinning **Fans** to increase your score.

### ⌨️ Controls

  - **Arrow Keys:** Move the AC unit up, down, left, and right.
  - **Left Shift:** Activate the **Blast** ability (when ready). This freezes all heaters for a few seconds.
  - **P:** Pause and resume the game.
  - **Spacebar:** Start the game from the title screen.
  - **R:** Restart the game after getting a game over.

-----

## 🛠️ Installation & Setup

To run this game on your local machine, follow these steps.

### ✅ Prerequisites

  - Python 3.7+
  - Pip (Python's package installer)

### 1\. Clone the Repository

First, clone this repository to your local machine or simply download the source code.

```bash
git clone https://github.com/SatChittAnand/gamigy-app.git
cd gamigy-app
```

### 2\. Install Dependencies

Install the required Python libraries using pip. ⚙️

```bash
pip install pygame python-dotenv web3 eth_account
```

### 3\. Place Assets

Make sure the following asset files are in the same directory as the Python script: 🖼️

  - `ac.png`
  - `heater.png`
  - `fan.png`
  - `collect.wav`
  - `lose.wav`

### 4\. Run the Game

You can now run the game\! ▶️

```bash
python game_script.py
```

*(Replace `game_script.py` with the actual name of the Python file).*

-----

## 🌐 Web3 Configuration (Optional)

If you want to enable the on-chain high score submission, you need to set up a `.env` file.

1.  **Create a `.env` file** 📄 in the same directory as the game script.

2.  **Add the following variables** to the file, replacing the placeholder values with your own:

    ```env
    # URL for your Ethereum node (e.g., from Infura or Alchemy)
    RPC_URL="https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"

    # The private key of the account that will pay for the transaction gas
    PRIVATE_KEY="YOUR_WALLET_PRIVATE_KEY"

    # The public address of the account above
    SIGNER_ADDRESS="YOUR_WALLET_PUBLIC_ADDRESS"

    # The address of the deployed smart contract
    CONTRACT_ADDRESS="YOUR_DEPLOYED_CONTRACT_ADDRESS"
    ```

> **⚠️ Security Warning:** Never commit your `.env` file or share your private key publicly.

3.  **Deploy the Smart Contract:** You need a simple smart contract deployed on your target network with a function to store scores. Here is a basic example using Solidity: 📜

    ```solidity
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.0;

    contract HighScore {
        address public owner;
        uint256 public highestScore;
        address public topPlayer;

        constructor() {
            owner = msg.sender;
        }

        // Simple function to allow anyone to submit a score.
        // In a real-world scenario, you might add more security.
        function submitScore(uint256 score) public {
            // A simple check: only update if the new score is higher.
            if (score > highestScore) {
                highestScore = score;
                topPlayer = msg.sender;
            }
        }
    }
    ```

If the `.env` file is not present or the variables are not set, the game will run perfectly fine with only local high score saving.

Happy Gaming\! 😊
