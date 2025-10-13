const protocol = location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(`${protocol}://${location.host}/ws/room/${roomId}/?role=${role}`);

const playingCards = {
    '2 of Spades': '/static/app/img/playing_cards/2_of_spades.png',
    '3 of Spades': '/static/app/img/playing_cards/3_of_spades.png',
    '4 of Spades': '/static/app/img/playing_cards/4_of_spades.png',
    '5 of Spades': '/static/app/img/playing_cards/5_of_spades.png',
    '6 of Spades': '/static/app/img/playing_cards/6_of_spades.png',
    '7 of Spades': '/static/app/img/playing_cards/7_of_spades.png',
    '8 of Spades': '/static/app/img/playing_cards/8_of_spades.png',
    '9 of Spades': '/static/app/img/playing_cards/9_of_spades.png',
    '10 of Spades': '/static/app/img/playing_cards/10_of_spades.png',
    'Jack of Spades': '/static/app/img/playing_cards/jack_of_spades.png',
    'Queen of Spades': '/static/app/img/playing_cards/queen_of_spades.png',
    'King of Spades': '/static/app/img/playing_cards/king_of_spades.png',
    'Ace of Spades': '/static/app/img/playing_cards/ace_of_spades.png',

    '2 of Hearts': '/static/app/img/playing_cards/2_of_hearts.png',
    '3 of Hearts': '/static/app/img/playing_cards/3_of_hearts.png',
    '4 of Hearts': '/static/app/img/playing_cards/4_of_hearts.png',
    '5 of Hearts': '/static/app/img/playing_cards/5_of_hearts.png',
    '6 of Hearts': '/static/app/img/playing_cards/6_of_hearts.png',
    '7 of Hearts': '/static/app/img/playing_cards/7_of_hearts.png',
    '8 of Hearts': '/static/app/img/playing_cards/8_of_hearts.png',
    '9 of Hearts': '/static/app/img/playing_cards/9_of_hearts.png',
    '10 of Hearts': '/static/app/img/playing_cards/10_of_hearts.png',
    'Jack of Hearts': '/static/app/img/playing_cards/jack_of_hearts.png',
    'Queen of Hearts': '/static/app/img/playing_cards/queen_of_hearts.png',
    'King of Hearts': '/static/app/img/playing_cards/king_of_hearts.png',
    'Ace of Hearts': '/static/app/img/playing_cards/ace_of_hearts.png',

    '2 of Diamonds': '/static/app/img/playing_cards/2_of_diamonds.png',
    '3 of Diamonds': '/static/app/img/playing_cards/3_of_diamonds.png',
    '4 of Diamonds': '/static/app/img/playing_cards/4_of_diamonds.png',
    '5 of Diamonds': '/static/app/img/playing_cards/5_of_diamonds.png',
    '6 of Diamonds': '/static/app/img/playing_cards/6_of_diamonds.png',
    '7 of Diamonds': '/static/app/img/playing_cards/7_of_diamonds.png',
    '8 of Diamonds': '/static/app/img/playing_cards/8_of_diamonds.png',
    '9 of Diamonds': '/static/app/img/playing_cards/9_of_diamonds.png',
    '10 of Diamonds': '/static/app/img/playing_cards/10_of_diamonds.png',
    'Jack of Diamonds': '/static/app/img/playing_cards/jack_of_diamonds.png',
    'Queen of Diamonds': '/static/app/img/playing_cards/queen_of_diamonds.png',
    'King of Diamonds': '/static/app/img/playing_cards/king_of_diamonds.png',
    'Ace of Diamonds': '/static/app/img/playing_cards/ace_of_diamonds.png',

    '2 of Clubs': '/static/app/img/playing_cards/2_of_clubs.png',
    '3 of Clubs': '/static/app/img/playing_cards/3_of_clubs.png',
    '4 of Clubs': '/static/app/img/playing_cards/4_of_clubs.png',
    '5 of Clubs': '/static/app/img/playing_cards/5_of_clubs.png',
    '6 of Clubs': '/static/app/img/playing_cards/6_of_clubs.png',
    '7 of Clubs': '/static/app/img/playing_cards/7_of_clubs.png',
    '8 of Clubs': '/static/app/img/playing_cards/8_of_clubs.png',
    '9 of Clubs': '/static/app/img/playing_cards/9_of_clubs.png',
    '10 of Clubs': '/static/app/img/playing_cards/10_of_clubs.png',
    'Jack of Clubs': '/static/app/img/playing_cards/jack_of_clubs.png',
    'Queen of Clubs': '/static/app/img/playing_cards/queen_of_clubs.png',
    'King of Clubs': '/static/app/img/playing_cards/king_of_clubs.png',
    'Ace of Clubs': '/static/app/img/playing_cards/ace_of_clubs.png',

    'reverse': '/static/app/img/playing_cards/reverse2-copy.png',
};


const currentActionHandlers = {
    fold: null,
    check: null,
    call: null,
    raise: null,
};

let yourPosition = null;

socket.onopen = () => {
    console.log("WebSocket connection established.");
    socket.send(JSON.stringify({
        type: "init_new_player",
    }));
}

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Message from server:", data);

    switch (data.type) {
        case 'init_participant':
            yourPosition = data.your_position;
            initParticipant(data.players);
            break;
        case 'init_observer':
            initObserver(data.players);
            break;
        case 'new_player':
            newPlayer(data.position, data.username, data.chip_count);
            break;
        case 'player_left':
            deletePlayer(data.position);
            break;
        case 'player_bet':
            playerBet(data.position, data.amount, data.chip_count, data.pot);
            break;
        case 'dealt_cards':
            dealtCards(data.cards, data.active_positions);
            break;
        case 'player_turn':
            playerTurn(data.username);
            break;
        case 'your_turn':
            yourTurn(data.current_bet, data.player_bet, data.chip_count, data.pot);
            break;
        case 'board_cards':
            boardCards(data.cards);
            break;
        case 'clear_betting':
            clearBetting();
            break;
        case 'hand_value':
            handValue(data.hand_value, data.hand_cards);
            break;
        case 'player_checked':
            playerChecked(data.position);
            break;
        case 'player_folded':
            playerFold(data.position);
            break;
        case 'showdown':
            showdown(data.hands)
            break;
        case 'round_winner':
            roundWinner(data.winner_positions, data.amount_won);
            break;
        case 'reset':
            reset(data.chip_counts);
            break;
        case 'action_error':
            // console.error(data.message);
            alert(data.message);
            break;
        default:
            console.error("Unknown message type:", data.type);
    }
};

socket.onerror = (error) => {
    messagesDiv = document.querySelector(".room-info");
    paragraph = document.createElement("p");
    paragraph.textContent = `Połączenie websocket nie powiodło się`;
    messagesDiv.appendChild(paragraph);
    console.error("WebSocket error:", error);

    setTimeout(() => {
        window.location.href = '/rooms';
    }, 4000);
}

// const relativePosition = (position) => {
//     return position - yourPosition >= 0 ? position - yourPosition : position - yourPosition + maxPlayers;
// }

const relativePosition = (position) => {
    const mapping = {
        0: 0,
        1: 4,
        2: 2,
        3: 6,
        4: 1,
        5: 7,
        6: 3,
        7: 5
    }
    const shift = maxPlayers - mapping[yourPosition];
    return (mapping[position] + shift) % maxPlayers;
}

/* Initialize players on the board on relative positions
 user position is 0, need to transform from server position to relative position
*/
const initParticipant = (players) => {
    const numberOfPlayers = Object.keys(players).length;
    const playerCountDiv = document.getElementById("current-players-count");
    playerCountDiv.textContent = `${numberOfPlayers}`;
    const entryButton = document.getElementById("entry-button");
    entryButton.textContent = "Leave";
    entryButton.addEventListener('click', leaveGame);
    for (const pos in players) {
        const relativePos = relativePosition(pos);
        const playerName = players[pos].username;
        const playerCards = players[pos].cards;
        let card1, card2;
        if (playerCards) {
            // cardsHTML = playerCards.join(', ');
            card1 = document.createElement("img");
            card1.src = playingCards[playerCards[0]];
            card1.alt = playerCards[0];
            card2 = document.createElement("img");
            card2.src = playingCards[playerCards[1]];
            card2.alt = playerCards[1];
        }
        const seatDiv = document.getElementById(`seat-${relativePos}`);
        if (seatDiv) {
            const playerCardsDiv = seatDiv.querySelector('.player-cards');
            const playerInfoDiv = seatDiv.querySelector('.player-info');

            if (card1 && card2) {
                playerCardsDiv.appendChild(card1);
                playerCardsDiv.appendChild(card2);
            }
            playerInfoDiv.innerHTML = `
                ${playerName}
                <span class="chips">${players[pos].chip_count}</span>
                <span class="bet"></span>`;
        }
    }

    const actionPanel = document.querySelector(".action-panel");
    actionPanel.querySelector("#playerChips").textContent = `${players[yourPosition].chip_count}`;
    actionPanel.querySelector("div").hidden = false;
}

const initObserver = (players) => {
    const playerCountDiv = document.getElementById("current-players-count");
    playerCountDiv.textContent = `${Object.keys(players).length}`;
    const entryButton = document.getElementById("entry-button");
    entryButton.textContent = "Join";
    entryButton.addEventListener('click', joinGame);
    for (const pos in players) {
        const playerName = players[pos].username;
        const playerCards = players[pos].cards;
        let card1, card2;

        if (playerCards) {
            // cardsHTML = playerCards.join(', ');
            card1 = document.createElement("img");
            card1.src = playingCards[playerCards[0]];
            card1.alt = playerCards[0];
            card2 = document.createElement("img");
            card2.src = playingCards[playerCards[1]];
            card2.alt = playerCards[1];
        }
        const seatDiv = document.getElementById(`seat-${pos}`);
        if (seatDiv) {
            const playerCardsDiv = seatDiv.querySelector('.player-cards');
            const playerInfoDiv = seatDiv.querySelector('.player-info');

            if (card1 && card2) {
                playerCardsDiv.appendChild(card1);
                playerCardsDiv.appendChild(card2);
            }
            playerInfoDiv.innerHTML = `
                ${playerName}
                <span class="chips">${players[pos].chip_count}</span>
                <span class="bet"></span>`;
        }
    }
}

const leaveGame = () => { // leave game as participant and become observer
    document.getElementById('entry-button').removeEventListener('click', leaveGame);
  const url = new URL(window.location.href);
    url.searchParams.set('role', 'observer');
    window.location.href = url.toString();
}



const joinGame = () => { // join game as participant and become participant
    document.getElementById('entry-button').removeEventListener('click', joinGame);
    const url = new URL(window.location.href);
    url.searchParams.set('role', 'participant');
    window.location.href = url.toString();
}

const deletePlayer = (position) => {
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        const playerCardsDiv = seatDiv.querySelector('.player-cards');
        const playerInfoDiv = seatDiv.querySelector('.player-info');
        playerCardsDiv.innerHTML = ``;
        playerInfoDiv.textContent = ``;
    }
    const playerCountDiv = document.getElementById("current-players-count");
    const currentCount = parseInt(playerCountDiv.textContent);
    playerCountDiv.textContent = `${currentCount - 1}`;
}

const newPlayer = (position, username, chip_count) => {
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        const playerCardsDiv = seatDiv.querySelector('.player-cards');
        const playerInfoDiv = seatDiv.querySelector('.player-info');

        playerCardsDiv.innerHTML = ``;
        playerInfoDiv.innerHTML = `
            ${username}
            <span class="chips">${chip_count}</span>
            <span class="bet"></span>`;
    }
    const playerCountDiv = document.getElementById("current-players-count");
    const currentCount = parseInt(playerCountDiv.textContent);
    playerCountDiv.textContent = `${currentCount + 1}`;
}

const playerBet = (position, amount, chip_count, pot) => {
    if (position === yourPosition) {
        const actionPanel = document.querySelector(".action-panel");
        actionPanel.querySelector("#playerChips").textContent = `${chip_count}`;
    }
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        const chipsSpan = seatDiv.querySelector(".chips");
        if (chipsSpan) {
            chipsSpan.textContent = `${chip_count}`;
        }
        const betSpan = seatDiv.querySelector(".bet");
        if (betSpan) {
            betSpan.textContent = `Zakład: ${amount}`;
        }
    }
    const potDiv = document.getElementById("pot-size");
    potDiv.textContent = `${pot}`;
}

const dealtCards = (cards, active_positions) => {
    /* Show cards dealt to player and simulate dealing hidden cards to opponents */
    const seatDiv = document.getElementById(`seat-0`);
    if (seatDiv) {
        const playerCardsDiv = seatDiv.querySelector(".player-cards");
        if (playerCardsDiv) {
            // cardsSpan.textContent = cards.join(', ');
            cards.forEach(card => {
                const img = document.createElement("img");
                img.src = playingCards[card];
                img.alt = card;
                playerCardsDiv.appendChild(img);
            })
        }
    }
    for (const pos of active_positions) {
        if (pos !== yourPosition) {
            const relativePos = relativePosition(pos);
            const seatDiv = document.getElementById(`seat-${relativePos}`);
            if (seatDiv) {
                const playerCardsDiv = seatDiv.querySelector(".player-cards");
                if (playerCardsDiv) {
                    playerCardsDiv.innerHTML = ``;
                    for (let i = 0; i < 2; i++) {
                        const img = document.createElement("img")
                        img.src = '/static/app/img/playing_cards/reverse2-copy.png';
                        img.alt = 'reverse';
                        playerCardsDiv.appendChild(img);
                    }
                }
            }
        }
    }
}

const boardCards = (cards) => {
    const boardDiv = document.getElementById("board-cards");
    for (const card of cards) {
        const cardDiv = document.createElement("div");
        cardDiv.classList.add("board-card");
        cardDiv.innerHTML = `
            <img src="${playingCards[card]}" alt="${card}">
        `;
        boardDiv.appendChild(cardDiv);
    }
}

const playerTurn = (username) => {
    const roomInfoDiv = document.querySelector(".room-info");
    const actingPlayerInfo = roomInfoDiv.querySelector("#acting-player")
    actingPlayerInfo.textContent = `Kolej gracza: ${username}`
}

const yourTurn = (current_bet, your_bet, your_chip_count, pot) => {
    const seatDiv = document.getElementById(`seat-0`);
    if (seatDiv) {
        const chipsSpan = seatDiv.querySelector(".chips");
        if (chipsSpan) {
            chipsSpan.textContent = `${your_chip_count}`;
        }
    }
    const actionPanel = document.querySelector(".action-panel");
    const buttonsDiv = actionPanel.querySelector(".action");
    buttonsDiv.hidden = false;
    buttonsDiv.classList.add("d-flex");
    actionPanel.querySelector("#playerChips").textContent = your_chip_count || '';

    // activate buttons
    const foldButton = buttonsDiv.querySelector(".fold");
    const checkButton = buttonsDiv.querySelector(".check");
    const callButton = buttonsDiv.querySelector(".call");
    const raiseButton = buttonsDiv.querySelector(".raise");
    const raiseInput = buttonsDiv.querySelector(".raise-input");
    const raiseSlider = buttonsDiv.querySelector(".raise-slider");

    // remove previous event listeners
    if (currentActionHandlers.fold) {
        foldButton.removeEventListener('click', currentActionHandlers.fold);
    }
    if (currentActionHandlers.check) {
        checkButton.removeEventListener('click', currentActionHandlers.check);
    }
    if (currentActionHandlers.call) {
        callButton.removeEventListener('click', currentActionHandlers.call);
    }
    if (currentActionHandlers.raise) {
        raiseButton.removeEventListener('click', currentActionHandlers.raise);
    }

    // reset buttons states
    checkButton.disabled = true;
    callButton.disabled = true;
    raiseButton.disabled = true;
    callButton.textContent = 'Call';

    // update max values for input
    raiseInput.min =  (current_bet - your_bet) + 1; // minimum raise is call + 1
    raiseInput.max = your_chip_count;
    raiseInput.value = raiseInput.min;
    raiseSlider.min = raiseInput.min;
    raiseSlider.max = raiseInput.max;
    raiseSlider.value = raiseInput.min;

    // set event listeners for buttons
    currentActionHandlers.fold = () => {
        socket.send(JSON.stringify({
            type: "player_action",
            action: "fold",
        }));
        buttonsDiv.hidden = true;
        buttonsDiv.classList.remove("d-flex");
    };
    foldButton.addEventListener('click', currentActionHandlers.fold, {once: true});

    if (current_bet === your_bet) {
        currentActionHandlers.check = () => {
            socket.send(JSON.stringify({
                type: "player_action",
                action: "call",
                amount: 0,
            }));
            buttonsDiv.hidden = true;
            buttonsDiv.classList.remove("d-flex");
        };
        checkButton.addEventListener('click', currentActionHandlers.check, {once: true});
        checkButton.disabled = false;
    }

    if (your_chip_count >= current_bet - your_bet) {
        currentActionHandlers.call = () => {
            socket.send(JSON.stringify({
                type: "player_action",
                action: "call",
                amount: current_bet - your_bet,
            }));
            buttonsDiv.hidden = true;
            buttonsDiv.classList.remove("d-flex");
        }
        callButton.addEventListener('click', currentActionHandlers.call, {once: true});
        callButton.disabled = false;

        if (your_chip_count > current_bet - your_bet) {
            currentActionHandlers.raise = () => {
                const raiseAmount = parseInt(raiseInput.value);
                if (raiseAmount >= raiseInput.min && raiseAmount <= raiseInput.max) {
                    socket.send(JSON.stringify({
                        type: "player_action",
                        action: "raise",
                        amount: raiseAmount,
                    }));
                    buttonsDiv.hidden = true;
                    buttonsDiv.classList.remove("d-flex");
                } else {
                    alert(`Nieprawidłowa kwota podbicia. Kwota musi być pomiędzy ${raiseInput.min} a ${raiseInput.max}.`);
                }
            }
            raiseButton.addEventListener('click', currentActionHandlers.raise, {once: true});
            raiseButton.disabled = false;
        }
    }
    else {
        raiseButton.disabled = true;
        // all in
        currentActionHandlers.call = () => {
            socket.send(JSON.stringify({
                type: "player_action",
                action: "call",
                amount: your_chip_count,
            }));
            buttonsDiv.hidden = true;
            buttonsDiv.classList.remove("d-flex");
        }
        callButton.textContent = `All in (${your_chip_count})`;
        callButton.addEventListener('click', currentActionHandlers.call, {once: true});
    }
}

const clearBetting = () => {
    const roomInfoDiv = document.querySelector(".room-info");
    const actingPlayerInfo = roomInfoDiv.querySelector("#acting-player")
    actingPlayerInfo.textContent = ``;

    const tableDiv = document.getElementById("table");
    for (const seat of tableDiv.querySelectorAll('.seat')) {
        const betSpan = seat.querySelector(".bet");
        if (betSpan) {
            betSpan.textContent = ``;
        }
    }
}

const playerChecked = (position) => {
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        const betSpan = seatDiv.querySelector(".bet");
        if (betSpan) {
            betSpan.textContent = `Czekam`;
        }
    }
}

const playerFold = (position) => {
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        const betSpan = seatDiv.querySelector(".bet");
        if (betSpan) {
            betSpan.textContent = `Pas`;
        }
        const cardsSpan = seatDiv.querySelector(".cards");
        if (cardsSpan) {
            cardsSpan.textContent = ``;
        }
    }
}

const showdown = (hands) => {
    const roomInfoDiv = document.querySelector(".room-info");
    const actingPlayerInfo = roomInfoDiv.querySelector("#acting-player")
    actingPlayerInfo.textContent = ``;
    for (const position in hands) {
        const relativePos = relativePosition(position);
        const hand = hands[position];
        const seatDiv = document.getElementById(`seat-${relativePos}`);
        if (seatDiv) {
            const cardsSpan = seatDiv.querySelector(".cards");
            if (cardsSpan) {
                cardsSpan.textContent = hand.join(', ');
            }
        }
    }
}

const roundWinner = (winner_positions, amount_won) => {
    for (const position of winner_positions) {
        const relativePos = relativePosition(position);
        const seatDiv = document.getElementById(`seat-${relativePos}`);
        if (seatDiv) {
            const betSpan = seatDiv.querySelector(".bet");
            if (betSpan) {
                betSpan.textContent = `Wygrywa: ${amount_won} chips`;
            }
        }
    }
}

const reset = (chip_counts) => {
    const actionPanel = document.querySelector(".action-panel");
    const buttonsDiv = actionPanel.querySelector(".action");
    const potDiv = document.getElementById("pot-size");
    const boardDiv = document.getElementById("board-cards");
    const tableDiv = document.getElementById("table");
    const actingPlayerInfo = document.querySelector(".room-info #acting-player");
    const playerHandDiv = actionPanel.querySelector("#playerHand");

    actingPlayerInfo.textContent = ``;
    playerHandDiv.textContent = ``;
    buttonsDiv.hidden = true;
    boardDiv.textContent = ``;
    potDiv.textContent = ``;

    for (const seat of tableDiv.querySelectorAll('.seat')) {
        const playerCardsDiv = seat.querySelector(".player-cards");
        if (playerCardsDiv) {
            playerCardsDiv.innerHTML = ``;
        }
        const betSpan = seat.querySelector(".bet");
        if (betSpan) {
            betSpan.textContent = ``;
        }
    }
    for (const pos in chip_counts) {
        const relativePos = relativePosition(pos);
        const seatDiv = document.getElementById(`seat-${relativePos}`);
        if (seatDiv) {
            const chipsSpan = seatDiv.querySelector(".chips");
            if (chipsSpan) {
                chipsSpan.textContent = `${chip_counts[pos]}`;
            }
        }
    }

}

const handValue = (hand_value, hand_cards) => {
    const actionPanel = document.querySelector(".action-panel");
    const playerHandDiv = actionPanel.querySelector("#playerHand");
    switch (hand_value) {
        case 'high_card':
            const highCard = hand_cards[0].match(/^(\w+)/)[1];
            playerHandDiv.textContent = `${highCard} high`;
            break;
        case 'pair':
            const pair = hand_cards[0].match(/^(\w+)/)[1];
            playerHandDiv.textContent = `pair of ${pair}s`;
            break;
        case 'two_pair':
            const pair1 = hand_cards[0].match(/^(\w+)/)[1];
            const pair2 = hand_cards[1].match(/^(\w+)/)[1];
            playerHandDiv.textContent = `two pairs of ${pair1}s and ${pair2}s`;
            break;
        case 'three_of_kind':
            const threeOfKind = hand_cards[0].match(/^(\w+)/)[1];
            playerHandDiv.textContent = `three of a kind of ${threeOfKind}s`;
            break;
        case 'straight':
            const highCardStraight = hand_cards[0].match(/^(\w+)/)[1];
            playerHandDiv.textContent = `straight ${highCard} high`;
            break;
        case 'flush':
            const highCardFlush = hand_cards[0].match(/^(\w+)/)[1];
            playerHandDiv.textContent = `flush ${highCard} high`;
            break;
        case 'full_house':
            const threeOfKindFlush = hand_cards[0].match(/^(\w+)/)[1];
            const pairFlush = hand_cards[1].match(/^(\w+)/)[1];
            playerHandDiv.textContent = `full house of ${threeOfKindFlush}s and ${pairFlush}s`;
            break;
        case 'four_of_kind':
            const fourOfKind = hand_cards[0].match(/^(\w+)/)[1];
            playerHandDiv.textContent = `four of a kind of ${fourOfKind}s`;
            break;
        case 'straight_flush':
            const highCardStraightFlush = hand_cards[0].match(/^(\w+)/)[1];
            playerHandDiv.textContent = `straight flush ${highCard} high`;


    }

}
