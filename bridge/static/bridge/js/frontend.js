const cardImages = {
    "Ah": "/static/img/playing_cards/ace_of_hearts.png",
    "2h": "/static/img/playing_cards/2_of_hearts.png",
    "3h": "/static/img/playing_cards/3_of_hearts.png",
    "4h": "/static/img/playing_cards/4_of_hearts.png",
    "5h": "/static/img/playing_cards/5_of_hearts.png",
    "6h": "/static/img/playing_cards/6_of_hearts.png",
    "7h": "/static/img/playing_cards/7_of_hearts.png",
    "8h": "/static/img/playing_cards/8_of_hearts.png",
    "9h": "/static/img/playing_cards/9_of_hearts.png",
    "Th": "/static/img/playing_cards/10_of_hearts.png",
    "Jh": "/static/img/playing_cards/jack_of_hearts.png",
    "Qh": "/static/img/playing_cards/queen_of_hearts.png",
    "Kh": "/static/img/playing_cards/king_of_hearts.png",
  
    "Ad": "/static/img/playing_cards/ace_of_diamonds.png",
    "2d": "/static/img/playing_cards/2_of_diamonds.png",
    "3d": "/static/img/playing_cards/3_of_diamonds.png",
    "4d": "/static/img/playing_cards/4_of_diamonds.png",
    "5d": "/static/img/playing_cards/5_of_diamonds.png",
    "6d": "/static/img/playing_cards/6_of_diamonds.png",
    "7d": "/static/img/playing_cards/7_of_diamonds.png",
    "8d": "/static/img/playing_cards/8_of_diamonds.png",
    "9d": "/static/img/playing_cards/9_of_diamonds.png",
    "Td": "/static/img/playing_cards/10_of_diamonds.png",
    "Jd": "/static/img/playing_cards/jack_of_diamonds.png",
    "Qd": "/static/img/playing_cards/queen_of_diamonds.png",
    "Kd": "/static/img/playing_cards/king_of_diamonds.png",
  
    "As": "/static/img/playing_cards/ace_of_spades.png",
    "2s": "/static/img/playing_cards/2_of_spades.png",
    "3s": "/static/img/playing_cards/3_of_spades.png",
    "4s": "/static/img/playing_cards/4_of_spades.png",
    "5s": "/static/img/playing_cards/5_of_spades.png",
    "6s": "/static/img/playing_cards/6_of_spades.png",
    "7s": "/static/img/playing_cards/7_of_spades.png",
    "8s": "/static/img/playing_cards/8_of_spades.png",
    "9s": "/static/img/playing_cards/9_of_spades.png",
    "Ts": "/static/img/playing_cards/10_of_spades.png",
    "Js": "/static/img/playing_cards/jack_of_spades.png",
    "Qs": "/static/img/playing_cards/queen_of_spades.png",
    "Ks": "/static/img/playing_cards/king_of_spades.png",
  
    "Ac": "/static/img/playing_cards/ace_of_clubs.png",
    "2c": "/static/img/playing_cards/2_of_clubs.png",
    "3c": "/static/img/playing_cards/3_of_clubs.png",
    "4c": "/static/img/playing_cards/4_of_clubs.png",
    "5c": "/static/img/playing_cards/5_of_clubs.png",
    "6c": "/static/img/playing_cards/6_of_clubs.png",
    "7c": "/static/img/playing_cards/7_of_clubs.png",
    "8c": "/static/img/playing_cards/8_of_clubs.png",
    "9c": "/static/img/playing_cards/9_of_clubs.png",
    "Tc": "/static/img/playing_cards/10_of_clubs.png",
    "Jc": "/static/img/playing_cards/jack_of_clubs.png",
    "Qc": "/static/img/playing_cards/queen_of_clubs.png",
    "Kc": "/static/img/playing_cards/king_of_clubs.png",
    "reverse": "/static/img/playing_cards/reverse2-copy.png"
  }

  const suitSymbols = {
    "c" : "♣",
    "d" : "♦",
    "h" : "♥",
    "s" : "♠",
    'b' : "BA"

}

const suitColors = {
    "c" : "black",
    "d" : "red",
    "h" : "red",
    "s" : "black",
    'b' : "black"
}
  

const malloc_JS = (str) => {
    const lengthBytes = lengthBytesUTF8(str) + 1;
    const stringOnWasmHeap = _malloc(lengthBytes);
    stringToUTF8(str, stringOnWasmHeap, lengthBytes);
    return stringOnWasmHeap;
}

const delay = async (ms) => {
    return new Promise(resolve => {
        setTimeout(resolve, ms)
    })
}

const prepareTable = (declarer, serializedContract) => {
    document.querySelector('.open-modal-btn').style.display = 'none'
    const table = document.querySelector('.table').children
    const whoPlay = (declarer % 2 === 0) ? "My gramy" : "Oni grają"
    const serializedContractJSON = JSON.parse(UTF8ToString(serializedContract))
    const level = serializedContractJSON["level"]
    const trump = String.fromCharCode(serializedContractJSON["miano"])

    const ourTrick = document.createElement("span")
    ourTrick.innerText = 0
    ourTrick.id = "ourCount"
    ourTrick.style.fontWeight = "bold"

    const theirTrick = document.createElement("span")
    theirTrick.innerText = 0
    theirTrick.id = "theirCount"
    theirTrick.style.fontWeight = "bold"

    for (let i = 0; i < 4; i++) table[i].innerText = ''

    const centerInfo = table[4].lastElementChild
    centerInfo.innerHTML = ""

    const p1 = document.createElement("p")
    p1.innerText = whoPlay

    const p2 = document.createElement("p")
    p2.innerText = `Wysokość kontraktu: ${level}`

    const p3 = document.createElement("p")
    p3.style.color = suitColors[trump]
    p3.innerHTML = `Atut:\n ${suitSymbols[trump]}`
    p3.style.fontWeight = "bold"
    p3.style.backgroundColor = "white"
    p3.style.borderRadius = "30%"
    p3.style.fontSize = "20px"

    const p4 = document.createElement("p")
    p4.innerHTML = `Nasze lewy: `
    p4.appendChild(ourTrick)

    const p5 = document.createElement("p")
    p5.innerHTML = `Ich lewy: `
    p5.appendChild(theirTrick)

    centerInfo.appendChild(p1)
    centerInfo.appendChild(p2)
    centerInfo.appendChild(p3)
    centerInfo.appendChild(p4)
    centerInfo.appendChild(p5)
};


clearUpdateTable = (ourCount, theirCount) => {
    const table = document.querySelector('.table').children
    const ourCounter = document.getElementById("ourCount")
    const theirCounter = document.getElementById("theirCount")
    for (let i = 0; i < 4; i++) {
        table[i].innerText = ''
    }
    ourCounter.innerText = ourCount
    theirCounter.innerText = theirCount
}

const setPlayerTurn = (playerPos) => {
    document.querySelector(".turn-holder").innerText = `Tura gracza ${String.fromCharCode(playerPos)}`
}


// ****************************************** //

const removeCard = (currentPlayer, serializedCard, isVisible) => {
    const card = JSON.parse(UTF8ToString(serializedCard))
    const rank = String.fromCharCode(card["rank"])
    const suit = String.fromCharCode(card["suit"])
    const playersDivs = document.querySelectorAll(".player")
    if (isVisible) {  
        const playerCards = playersDivs[currentPlayer + 1].childNodes
        for (const card of playerCards) {
            if (card.value === rank + suit) {
                card.remove()
                break
            }
        }
    }
    else {
        const cardReverse = playersDivs[currentPlayer + 1].firstChild
        cardReverse.remove()
    }
}

const setHand = (playerNum, handJSON) => {
    const playersDivs = document.querySelectorAll(".player")
    const playerCardsDiv = playersDivs[playerNum + 1]
    playerCardsDiv.innerHTML = ''

    for (const card of handJSON) {
        const rank = String.fromCharCode(card["rank"])
        const suit = String.fromCharCode(card["suit"])

        /* TEXT VERSION
        const cardDiv = document.createElement("p")
        cardDiv.innerText = rank + suit
        cardDiv.classList.add("card")
        playerCardsDiv.appendChild(cardDiv)
        */

        const cardImg = document.createElement("img")
        cardImg.src = cardImages[`${rank + suit}`]
        cardImg.alt = rank + suit
        cardImg.value = rank + suit
        cardImg.classList.add("card")
        cardImg.classList.add("card-averse")
        playerCardsDiv.appendChild(cardImg)
    }    
}

const setInitial = (playerHand) => {
    document.querySelector(".open-modal-btn").style.display = 'block'
    const playersDivs = document.querySelectorAll(".player")
    const heroHandJSON = JSON.parse(UTF8ToString(playerHand))

    for (let i = 0; i < 4; i++) {
        const playerCardsDiv = playersDivs[i + 1]
        playerCardsDiv.innerHTML = ''
        if (i === 0) {
            setHand(i, heroHandJSON)
        }
        else {
            for (let i = 0; i < 13; i++) {
                /* TEXT VERSION
                const cardDiv = document.createElement("p")
                cardDiv.innerText = "Rewers"
                cardDiv.classList.add("card")
                playerCardsDiv.appendChild(cardDiv)
                */
                const cardImg = document.createElement("img")
                cardImg.src = cardImages["reverse"]
                cardImg.alt = "reverse"
                cardImg.value = "reverse"
                cardImg.classList.add("card")
                playerCardsDiv.appendChild(cardImg)
            }
        }
    }
    
}

const setAuctionState = async (serializedHighest, serializedCurrent, playerPosition) => {
    const highestBid = JSON.parse(UTF8ToString(serializedHighest))
    const currentBid = JSON.parse(UTF8ToString(serializedCurrent))

    const highestBidLevel = highestBid["level"]
    const highestBidSuit = String.fromCharCode(highestBid["miano"])
    const currentBidLevel = currentBid["level"]
    const currentBidSuit = String.fromCharCode(currentBid["miano"])
    const playerPosChar = String.fromCharCode(playerPosition)
    const centerInfo = document.querySelector(".info")
    centerInfo.innerText = (highestBidLevel > 0) ? `Najwyzsza odzywka: ${highestBidLevel} ${highestBidSuit}` : "Pas"

    const playerTable = document.querySelector(`.${playerPosChar}`)
    playerTable.innerHTML = ''
    const bidCard = document.createElement("div")
    bidCard.classList.add("bid-card") 
    bidCard.innerText = (currentBidLevel === 0) ? "PAS" : currentBidLevel + suitSymbols[currentBidSuit] 
    bidCard.style.color = suitColors[currentBidSuit]
    playerTable.appendChild(bidCard)
    await delay(2000) // simulate AI
}

const setPlayedCard = async (playerPosition, serializedCard) => {
    const playedCardJSON = JSON.parse(UTF8ToString(serializedCard))
    const cardRank = String.fromCharCode(playedCardJSON["rank"])
    const cardSuit = String.fromCharCode(playedCardJSON["suit"])
    const playerTable = document.querySelector(`.${String.fromCharCode(playerPosition)}`)
    playerTable.innerHTML = ''
    const cardImg = document.createElement("img")
    cardImg.src = cardImages[`${cardRank + cardSuit}`]
    cardImg.alt = cardRank + cardSuit
    cardImg.classList.add("card")
    playerTable.appendChild(cardImg)
    await delay(1000) // simulate AI
}

const setScore = (ourGames, ourPoints, ourAddPoints, theirGames, theirPoints, theirAddPoints) => {
    const ourGamesDiv = document.getElementById("myGames")
    const theirGamesDiv = document.getElementById("theirGames")
    const ourPointsDiv = document.getElementById("myAboveLine")
    const ourAddPointsDiv = document.getElementById("myUnderLine")
    const theirPointsDiv = document.getElementById("theirUnderLine")
    const theirAddPointsDiv = document.getElementById("theirAboveLine")

    ourGamesDiv.innerText = ourGames
    theirGamesDiv.innerText = theirGames

    ourPointsDiv.innerText = ourPoints
    theirPointsDiv.innerText = theirPoints

    ourAddPointsDiv.innerText = ourAddPoints
    theirAddPointsDiv.innerText = theirAddPoints

    modalResults.style.display = 'block'

}

const activateBidButtons = (serializedHighest) => {
    const suitOrder = {
        'c' : 0,
        'd' : 1,
        'h' : 2,
        's' : 3,
        'b' : 4
    }
    const bidButtons = document.querySelectorAll(".grid button")
    const minimalBid = JSON.parse(UTF8ToString(serializedHighest))
    const minimalLevel = minimalBid["level"]
    const minimalSuit = String.fromCharCode(minimalBid["miano"])

    bidButtons.forEach(button => {
        const buttonLevel = button.value[0]
        const buttonSuit = button.value[1]

        if ((buttonLevel > minimalLevel) ||
            (buttonLevel == minimalLevel && suitOrder[buttonSuit] > suitOrder[minimalSuit])) {
                button.disabled = false
            }
        else button.disabled = true
    })
    // openBtn.style.display = 'block'
}

const fetchCard = async (isHero) => {
    const playerCards = (isHero) ? document.querySelector(".south").childNodes : document.querySelector(".north").childNodes

    const clickPromise = new Promise(resolve => {
        const handler = (event) => {
            playerCards.forEach(card => {
                card.removeEventListener("click", handler)
            })
            resolve(event.target.value)
        }
        playerCards.forEach(card => {
            card.addEventListener("click", handler)
        })
    })

    const chosedCard = await clickPromise
    return chosedCard
}

const fetchPlayerBid = async () => {
    const passButton = document.querySelector(".pass-button")
    const bidButtons = document.querySelectorAll(".grid button:not([disabled])")
    const clickPromise = new Promise(resolve => {
        const handler = (event) => {
            passButton.removeEventListener("click", handler)
            bidButtons.forEach(button => {
                button.removeEventListener("click", handler)
            })
            modal.style.display = 'none'
            resolve(event.target.value)
        }
        passButton.addEventListener("click", handler)
        bidButtons.forEach(button => {
            button.addEventListener("click", handler)
        })
    })

    const chosedBid = await clickPromise
    return chosedBid
}

const downloadResults = () => {
    Module._writeResults()
    const data = FS.readFile("./results/results.txt")
    const blob = new Blob([data], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    link.download = 'results.txt'
    document.body.appendChild(link)
    link.click()
    link.remove()

    URL.revokeObjectURL(url)
}