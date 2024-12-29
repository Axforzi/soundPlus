const showMusicModal = (img) =>{
    const modal = document.querySelector('.artist-more');
    modal.classList.toggle('artist-more-show');
    
    modal.querySelector('img').src = '/static/img/music_covers/' + img;
}

// CLICK USER PROFILE
addEventListener('click', (event) => {
    const containerLogged = document.querySelector('.container-logged');
    if(containerLogged !== null){
        if(!containerLogged.contains(event.target)){
            containerLogged.classList.remove('container-logged-show');
        }
        else{
            containerLogged.classList.toggle('container-logged-show')
        }
    }
});

// PREVIEW IMG PROFILE / ACCOUNT
const imgProfile = (event) => {
    const file = event.target.files;

    let imgProfile = document.querySelector('.modal .preview-img');
    if (imgProfile.tagName === 'I'){ // CHECK IF THERE IS A PREVIUS IMG
        const img = document.createElement('img');
        img.classList.add('preview-img');
        imgProfile.replaceWith(img);

        imgProfile = document.querySelector('.modal .preview-img');
    }

    if (file) {
        // LOAD IMG ON DOM 
        const fileReader = new FileReader();
        fileReader.onload = e => {
            imgProfile.src = e.target.result
        }
        fileReader.readAsDataURL(file[0]);
    }
}

// PREVIEW IMG ACCOUNT - CREATE ARTIST
const imgArtistPreview = (event) => {
    const file = event.target.files;

    if (file && file[0]) {
        const imgProfileContainer = document.querySelector('form .preview-img');
        const imgPreviewContainer = document.querySelector('.preview .preview-img');

        // DELETE PREVIOUS ELEMENTS
        imgProfileContainer.innerHTML = '';
        imgPreviewContainer.innerHTML = '';

        // CREATE ELEMENT IMG
        const imgProfile = document.createElement('img');
        const imgPreviewProfile = document.createElement('img');

        // ADD IMGS
        imgProfileContainer.appendChild(imgProfile);
        imgPreviewContainer.appendChild(imgPreviewProfile);

        // READ FILES AND ADD SRC
        const fileReader = new FileReader();
        fileReader.onload = e => {
            imgProfile.src = e.target.result;
            imgPreviewProfile.src = e.target.result;
        };
        fileReader.readAsDataURL(file[0]);
    }
}

// PREVIEW BACKGROUND ACCOUNT - CREATE ARTIST
const backgroundArtistPreview = (event) => {
    const file = event.target.files;

    let background = document.querySelector('.preview .preview-background');
    if (background.tagName === 'DIV'){ // CHECK IF THERE IS A PREVIUS IMG
        const img = document.createElement('img');
        img.classList.add('preview-background');
        background.outerHTML = img.outerHTML;

        background = document.querySelector('.preview .preview-background');
    }
    if (file) {
        // LOAD IMG ON DOM 
        const fileReader = new FileReader();
        fileReader.onload = e => {
            background.src = e.target.result;
        }
        fileReader.readAsDataURL(file[0]);
    }
}

const previewTitle = (event) => {
    document.querySelector('.preview .preview-title').textContent = event.target.value;
}

addEventListener('htmx:beforeRequest', (e) => {
    if (e.target.matches('.btn-add-list') || e.target.matches('.add-library') ||
        e.target.matches('.btn-follow') || e.target.matches('#newList')){
        document.querySelector('.loading.library').style.opacity = '1';
    }
    
    // SAVE PREVIUS SONG BEFORE RANDOM
    if (e.target.matches('.random')){
        if (!e.target.classList.contains('active')){
            previusSelected = document.querySelector('.play-queue .song.selected').dataset.id;
        } else{
            previusSelected = null;
        }
    }
});

addEventListener('htmx:afterRequest', (e) => {
    // SCROLL AFTER CHANGE OF PAGE
    if(!e.target.matches('.btn-more-music') && !e.target.matches('.btn-play') && !e.target.matches('.add-queue') &&
       !e.target.matches('.play-music') && !e.target.matches('.add') && !e.target.matches('.btns-container') &&
       !e.target.matches('.lists')){
        document.querySelector('.content').scroll({top: 0, behavior: 'smooth'});
    }

    // HIDE PLAY QUEUE
    if (e.target.matches('.btn-home') || e.target.matches('.btn-search') || e.target.matches('.library-element') || e.target.matches('.link-artist')) {
        setTimeout(() => {
            document.querySelector('.play-queue').classList.remove('show-play-queue');
            const btnQueue = document.querySelector('.btn-queue span');
            btnQueue.style.color = 'white';
        }, 300);
    }

    // LOAD QUEUE AND PLAY MUSIC
    if(e.target.matches('.btn-play') || e.target.parentNode.matches('.btn-play') || e.target.matches('.play-music')){
        loadMusics();
        loadMusic();
    }

    // UPDATE QUEUE
    if(e.target.matches('.add-queue')){
        const empty = document.querySelector('.songs-queue tbody .empty');
        if(empty){
            empty.remove();
            document.querySelector('.player').classList.add('show');
            loadMusics();
            loadMusic();
        } else{
            loadMusics();
        }
    }

    // SELECT SONG AFTER RANDOM
    if (e.target.querySelector('.random.loading-music')){
        const currentMusicEl = document.querySelector('.songs-queue tbody tr');
        document.querySelector('.songs-queue tbody tr').classList.toggle('selected');
        document.querySelector('.player .random.loading-music').classList.toggle('loading-music');

        // SET RANDOM URL's
        const randomBtn = document.querySelector('.player .controls .random');
        if (randomBtn.getAttribute('hx-post').search('\\?') !== -1){
            randomBtn.setAttribute('hx-post', randomBtn.getAttribute('hx-post') + '&currentMusic=' + currentMusicEl.dataset.id);
        } else{
            randomBtn.setAttribute('hx-post', randomBtn.getAttribute('hx-post') + '?currentMusic=' + currentMusicEl.dataset.id);
        }
        htmx.process(randomBtn);

        loadMusics();
    }
    
    // DEACTIVATE INDICATOR
    document.querySelector('.loading.library').style.opacity = '0';
})

addEventListener('click', (e) => {
    if (e.target.matches('.cancel-list-form')){
        document.querySelector('.container-list-form').classList.toggle('show');
    }

    if (e.target.matches('.btn-play') || e.target.parentNode.matches('.btn-play') || e.target.matches('.play-music')){
        document.querySelector('.player').classList.add('show');
    }

    // SHOW MENU HEADER
    if (e.target.closest('.btn-menu')){
        document.querySelector('.header-nav').classList.toggle('header-nav-show');
        document.querySelector('.btn-menu').classList.toggle('btn-menu-show');
    }

    // SHOW CONTEXT MENU MUSIC 
    if (e.target.closest('.btn-more-music')){
        const button = e.target.parentNode
        const context = button.nextElementSibling;

         // CHECK CONTEXT
        if (document.querySelector('.show-context') &&
            document.querySelector('.show-context') !== context){
            document.querySelector('.show-context').classList.toggle('show-context');
        }
        
        if(!context.classList.contains('show-context')){
            // GET SIZE AND POSITION
            const buttonRect = button.getBoundingClientRect();
            const contextHeight = context.offsetHeight;
            const contextWidth = context.querySelector('.add-list .lists').offsetWidth + context.offsetWidth;
            let contentRect = '';

            // GET CONTAINER FROM CONTEXT MENU
            if (document.querySelector('.play-queue').contains(button)) {
                contentRect = document.querySelector('.play-queue').getBoundingClientRect();
            }
            else{
                contentRect = document.querySelector('.content').getBoundingClientRect();
            }

            const spaceTop = contentRect.bottom - buttonRect.bottom;
            const spaceBottom = buttonRect.top - contentRect.top;
            const spaceRight = contentRect.right - buttonRect.right;

            if (spaceTop <= contextHeight){
                context.style.bottom = '50%';
                context.style.top = 'unset';
            } else if (spaceBottom <= contextHeight){
                context.style.top = '50%';
                context.style.bottom = 'unset';
            }
        }

        context.classList.toggle('show-context');
        
        context.addEventListener('mouseleave', () => {
            context.classList.remove('show-context')
        });

    } else{
        if(!e.target.closest('.show-context') && document.querySelector('.show-context')){
            document.querySelector('.show-context').classList.toggle('show-context');
        }
    }

    // DELETE FROM QUEUE 
    if(e.target.matches('.remove-queue')){
        removeMusicQueue(e.target.closest('.song'));
    }
})


// SLIDERS
let swiper = new Swiper('.swiper', {
    loop: true,
    slidesPerView: 2,
  
    // Navigation arrows
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },

    breakpoints: {
        450: {
            slidesPerView: 3,
        },
        700: {
            slidesPerView: 4
        },
        800: {
            slidesPerView: 6
        },
        1000:{
            slidesPerView: 4
        },
        1200:{
            slidesPerView: 5
        },
        1280:{
            slidesPerView: 6
        }
    }
});

// WARNINGS FILTER
const originalWarn = console.warn;
console.warn = function (msg, ...args) {
  if (typeof msg === 'string' && msg.includes('Swiper Loop Warning')) {
    return;
  }
  originalWarn.apply(console, [msg, ...args]);
};