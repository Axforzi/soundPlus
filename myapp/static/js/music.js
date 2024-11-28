const currentTimeEl = document.querySelector('.current-time');
const durationEl = document.querySelector('.player .duration');
const prevBtn = document.querySelector('.player .previus');
const nextBtn = document.querySelector('.player .next');
const playBtn = document.querySelector('.player .play');
const range = document.querySelector('.progress .container-cursor input[type="range"]');
const volume = document.querySelector('.btn-volume .container-cursor input[type="range"]');

// MUSIC PLAYER 
const music = new Audio();

let isPlaying = false;
let isDragging = false;
let previusSelected = null;
let musicsCount = 0;

const loadMusics = () =>{
    try {
        const musicElements = document.querySelectorAll('.songs-queue tbody tr');
        // UPDATE ID's
        musicElements.forEach((item, index) => {
            item.dataset.number = index;
        });

        musicsCount = musicElements.length-1;

        // CHECK IF THERE IS MUSIC ON QUEUE
        if(musicsCount+1 === 0){
            document.querySelector('.songs-queue tbody').innerHTML = '<tr class="song empty"> <td style="text-align: center;" colspan="6"> <h2> No hay canciones en la cola </h2> </td> </tr>'
        }
    } catch (err) {
        console.log(err);
    }
}
const loadMusic = (musicEl = document.querySelectorAll('.songs-queue tbody tr')[0]) => {
    // CHECK IF THERE IS MUSIC ON QUEUE
    if (musicsCount+1 === 0){
        // SET INFO
        document.querySelector('.player .info .name').textContent = "";
        document.querySelector('.player .info .artist-name').textContent = "";
        document.querySelector('.player img').src = "";

        // SET URL's
        document.querySelector('.player .info .artist-name').setAttribute('hx-get', ``);
        document.querySelector('.player .info .name').setAttribute('hx-get', ``);
        htmx.process(document.querySelector('.player .info .artist-name'));
        htmx.process(document.querySelector('.player .info .name'));

        // SET RANDOM URL's
        const randomBtn = document.querySelector('.player .controls .random');
        if (randomBtn.getAttribute('hx-post').search('\\?') !== -1){
            if (randomBtn.getAttribute('hx-post').search('&') !== -1) {
                randomBtn.setAttribute('hx-post', randomBtn.getAttribute('hx-post') + '&currentMusic=' + musicEl.dataset.id);
            } else{
                const urlRandom = randomBtn.getAttribute('hx-post').slice(0 ,randomBtn.getAttribute('hx-post').search('\\&'));
            }
        } else{
            randomBtn.setAttribute('hx-post', randomBtn.getAttribute('hx-post') + '?currentMusic=' + musicEl.dataset.id);
        }
        htmx.process(randomBtn);

        document.querySelector('.player .music').classList.toggle('show');
        music.src = '';

        isPlaying=false;
    }
    else{
        musicEl.classList.toggle('selected');

        // SET INFO
        document.querySelector('.player .info .name').textContent = musicEl.dataset.name;
        document.querySelector('.player .info .artist-name').textContent = musicEl.dataset.artist;
        document.querySelector('.player img').src = musicEl.querySelector('img').src;
    
        // SET URL's
        document.querySelector('.player .info .artist-name').setAttribute('hx-get', `/artist/${musicEl.dataset.artist}`);
        document.querySelector('.player .info .name').setAttribute('hx-get', `/artist/${musicEl.dataset.artist}/album/${musicEl.dataset.album}`);
        htmx.process(document.querySelector('.player .info .artist-name'));
        htmx.process(document.querySelector('.player .info .name'));

        // SET RANDOM URL's
        const randomBtn = document.querySelector('.player .controls .random');
        const hxurl = randomBtn.getAttribute('hx-post');
        if (hxurl.search('\\?') !== -1){
            if ((hxurl.search('\\&') === -1) && (hxurl.search('\\?current') === -1)) {
                randomBtn.setAttribute('hx-post', hxurl + '&currentMusic=' + musicEl.dataset.id);
            } else{
                if (hxurl.search('\\&') > 0){
                    const urlRandom = hxurl.slice(0 , hxurl.search('\\&'));
                    randomBtn.setAttribute('hx-post', urlRandom + '&currentMusic=' + musicEl.dataset.id);
                } else{
                    const urlRandom = hxurl.slice(0 , hxurl.search('\\?'));
                    randomBtn.setAttribute('hx-post', urlRandom + '?currentMusic=' + musicEl.dataset.id);
                }
            }
        } else{
            randomBtn.setAttribute('hx-post', randomBtn.getAttribute('hx-post') + '?currentMusic=' + musicEl.dataset.id);
        }
        htmx.process(randomBtn);
        
        // SHOW MUSIC DATA
        if (!document.querySelector('.player .music').classList.contains('show')) {
            document.querySelector('.player .music').classList.toggle('show');    
        }
        music.src = '/serve_music/' + musicEl.dataset.id;
        music.load();
        playMusic();
    }
}

const loadMetadata = (e) => {
    const duration = e.target.duration;
    const formatTime = (time) => String(Math.floor(time)).padStart(2, '0');
    durationEl.textContent = `${formatTime(duration/60)}:${formatTime(duration % 60)}`;
    currentTimeEl.textContent = "00:00";
}

const togglePlay = () =>{
    if (music.readyState !== 0){
        if(isPlaying){
            pauseMusic();
        }
        else{
            playMusic();
        }
    }
}

const playMusic = () => {
    isPlaying = true;
    playBtn.querySelector('span').textContent = 'pause';
    music.play();
}

const pauseMusic = () => {
    isPlaying = false;
    playBtn.querySelector('span').textContent = 'play_arrow';
    music.pause();
}

const nextMusic = () => {
    if(musicsCount+1!==0){
        const currentSongEl = document.querySelector('.songs-queue .song.selected');
        let newSongID = parseInt(currentSongEl.dataset.number)+1;
        let newSongEl = String();
        range.value = 0;

        if(newSongID > musicsCount){
            newSongEl = document.querySelector(`.songs-queue .song[data-number="0"]`);
            newSongID = 0;
        } else{
            newSongEl = document.querySelector(`.songs-queue .song[data-number="${newSongID}"]`);
        }

        currentSongEl.classList.toggle('selected');
        document.querySelector('.player .music').classList.toggle('show');

        setTimeout(() => {
            loadMusic(newSongEl);
            if(isPlaying){
                playMusic();
            }
        }, 300);
    }
}

const previusMusic = () =>{
    if(musicsCount+1!==0){
        const currentSongEl = document.querySelector('.songs-queue .song.selected');
        let newSongID = parseInt(currentSongEl.dataset.number)-1;
        let newSongEl = String();

        if(newSongID < 0){
            newSongEl = document.querySelector(`.songs-queue .song[data-number="${musicsCount}"]`);
            newSongID = musicsCount;
        } else{
            newSongEl = document.querySelector(`.songs-queue .song[data-number="${newSongID}"]`);
        }

        // CHANGE STYLE SELECTED SONG 
        currentSongEl.classList.toggle('selected');
        document.querySelector('.player .music').classList.toggle('show');

        setTimeout(() => {
            loadMusic(newSongEl);
            if(isPlaying){
                playMusic();
            }
        }, 300);
    }
}

const removeMusicQueue = (songEl) => {
    songEl.classList.toggle('removed');
    setTimeout(() => {
        // CHECK IF ELEMENT IS SELECTED BEFORE REMOVE
        if(songEl.classList.contains('selected')){
            const idMusic = songEl.dataset.number;
            songEl.remove();

            loadMusics();
            if(idMusic > musicsCount){
                loadMusic(document.querySelector(`.songs-queue .song[data-number="${idMusic-1}"]`));
            } else{
                loadMusic(document.querySelector(`.songs-queue .song[data-number="${idMusic}"]`));
            }

            if(isPlaying){
                playMusic();
            }
        } else{
            songEl.remove();

            loadMusics();
            if(isPlaying){
                playMusic();
            }
        }
    }, 500);
};

const selectMusicQueue = (newSongEl) =>{
    const currentSongEl = document.querySelector('.songs-queue .song.selected');
    currentSongEl.classList.toggle('selected');
    document.querySelector('.player .music').classList.toggle('show');

    setTimeout(() => {
        loadMusic(newSongEl);
        playMusic()
    }, 300)
};

const updateProgessBar = (e) => {
    if (!isDragging && music.readyState >= 2) {
        const { duration, currentTime } = music;
        range.value = (currentTime / duration) * 100;
        range.style.backgroundSize = (currentTime / duration) * 100 + "% 100%";
        updateTimeIndicators();
    }
};


const updateTimeIndicators = () =>{
    const { duration, currentTime } = music;
    const formatTime = (time) => String(Math.floor(time)).padStart(2, '0');
    durationEl.textContent = `${formatTime(duration/60)}:${formatTime(duration % 60)}`;
    durationEl.textContent = durationEl.textContent === "NaN:NaN" ? "00:00": `${formatTime(duration/60)}:${formatTime(duration % 60)}`;
    currentTimeEl.textContent = `${formatTime(currentTime/60)}:${formatTime(currentTime % 60)}`;
}

const setProgressBar = () => {
    if (music.readyState >= 2) {
        isDragging = true;
        updateTimeIndicators();

        if (music.paused) {
            const newPosition = (range.value / 100) * music.duration;
            music.currentTime = newPosition;
        }

        if (musicsCount + 1 === 0) {
            range.value = 0;
            currentTimeEl.textContent = "00:00";
        }
    }
};

const draggedProgressBar = () => {
    isDragging = false;
    if (music.readyState >= 2) {
        const newPosition = (range.value / 100) * music.duration;
        music.currentTime = newPosition;
        updateProgessBar();
    }
};


playBtn.addEventListener('click', togglePlay);
nextBtn.addEventListener('click', nextMusic);
prevBtn.addEventListener('click', previusMusic);
music.addEventListener('timeupdate', updateProgessBar);
music.addEventListener('loadedmetadata', loadMetadata);
music.addEventListener('ended', nextMusic);
range.addEventListener('input', setProgressBar);
range.addEventListener('change', draggedProgressBar);
volume.addEventListener('input', () => {
    music.volume = volume.value;
    if(music.volume === 0){
        document.querySelector('.btn-volume span').textContent = 'volume_off';
        volume.style.backgroundSize = '0 100%';
    } else{
        document.querySelector('.btn-volume span').textContent = 'volume_up';
        volume.style.backgroundSize = `${music.volume * 100}% 100%`;
    }
})

addEventListener('click', (e) => {
    if(e.target.matches('.play-music-queue')){
        selectMusicQueue(e.target.parentNode.parentNode);
    }
})

// EXTRA
const showQueue = (event) => {
    const playQueue = document.querySelector('.play-queue');
    const btnQueue = document.querySelector('.btn-queue span');

    if(!playQueue.classList.contains('show-play-queue')){
        btnQueue.style.color = 'var(--color-green)';
    } else{
        btnQueue.style.color = 'white';
    }
    playQueue.classList.toggle('show-play-queue');
}