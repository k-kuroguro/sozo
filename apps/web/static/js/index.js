const setEggShaking = (accumulatedScore) => {
   const egg = document.getElementById('egg');

   if (accumulatedScore > EVOLUTION_THRESHOLD) return;

   let rotation = 0;
   if (accumulatedScore > 0.9 * EVOLUTION_THRESHOLD) {
      rotation = 10;
   } else if (accumulatedScore > 0.75 * EVOLUTION_THRESHOLD) {
      rotation = 5;
   } else if (accumulatedScore > 0.5 * EVOLUTION_THRESHOLD) {
      rotation = 2;
   }

   egg.style.setProperty('--shake-rotation', `${rotation}deg`);
};

const evolveIfPossible = (accumulatedScore) => {
   if (accumulatedScore > EVOLUTION_THRESHOLD) {
      is_evolved = true;

      const egg = document.getElementById('egg');
      const pet = document.getElementById('pet');
      egg.style.display = 'none';
      pet.style.display = 'block';

      pet.classList.add('evolve');
      pet.addEventListener('animationend', () => {
         pet.classList.remove('evolve');
         pet.removeEventListener('animationend', () => { });
      });
   }
};

const restartPetAnimation = () => {
   const pet = document.getElementById('pet');
   pet.classList.remove('jump');
   window.requestAnimationFrame((time1) => {
      window.requestAnimationFrame((time2) => {
         pet.classList.add('jump');
      });
   });
};

const updateScores = (currentScore, accumulatedScore) => {
   document.getElementById('current-score').textContent = currentScore.toFixed(3);
   document.getElementById('accumulated-score').textContent = accumulatedScore.toFixed(3);
};

const penaltyFactorMap = {
   "IS_ABSENT": "離席",
   "IS_DROWSY": "眠気",
   "IS_LOOKING_AWAY": "よそ見"
};

const updatePenaltyFactorList = (penaltyFactors) => {
   const factorList = document.getElementById('penalty-factor-list');
   factorList.innerHTML = '';

   if (penaltyFactors.length > 0) {
      penaltyFactors.forEach(factor => {
         const li = document.createElement('li');
         li.textContent = penaltyFactorMap[factor];
         factorList.appendChild(li);
      });
   } else {
      const li = document.createElement('li');
      li.textContent = '特になし';
      factorList.appendChild(li);
   }
};

let is_jumping = false;
let restartHandler = () => {
   if (is_jumping) {
      restartPetAnimation();
   }
}
setInterval(restartHandler, 1500);

const createEventSource = () => {
   const es = new EventSource('/monitor');

   es.addEventListener('status_msg', function (event) {
      const data = JSON.parse(event.data.replaceAll("'", '"'))
      console.log(data)

      const currentScore = data["overall_score"]
      const accumulatedScore = data["accumulated_score"]
      const penaltyFactors = data["penalty_factor"]

      updateScores(currentScore, accumulatedScore);
      updatePenaltyFactorList(penaltyFactors);
      if (is_evolved) {
         if (currentScore > 90) {
            is_jumping = true;
         } else {
            is_jumping = false;
         }
      } else {
         setEggShaking(accumulatedScore);
         evolveIfPossible(accumulatedScore);
      }
   });
   es.addEventListener('error_msg', function (event) {
      const data = JSON.parse(event.data.replaceAll("'", '"'))
      console.log(data);
   });
   es.addEventListener('error', function (event) {
      console.log('Error', event);
   });
   es.addEventListener('open', function (event) { });

   return es;
};

es = createEventSource();
