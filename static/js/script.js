/* ==========================================
   ANAND SURGICALS
   SCRIPT.JS
========================================== */


/* ==========================
   AUTO SLIDER
========================== */

let slideIndex = 0;

const slides = document.querySelectorAll(".slide");

function showSlides(){

    slides.forEach(slide=>{
        slide.style.display="none";
    });

    slideIndex++;

    if(slideIndex > slides.length){

        slideIndex = 1;

    }

    if(slides.length>0){

        slides[slideIndex-1].style.display="block";

    }

}

showSlides();

setInterval(showSlides,3000);



/* ==========================
   LIVE SEARCH
========================== */

const searchInput = document.getElementById("searchInput");

const searchResults = document.getElementById("searchResults");

if(searchInput){

searchInput.addEventListener("keyup",function(){

    let keyword = this.value.trim();

    if(keyword.length<2){

        searchResults.innerHTML="";

        return;

    }

    fetch("/live_search?q="+encodeURIComponent(keyword))

    .then(response=>response.json())

    .then(data=>{

        let html="";

        data.forEach(item=>{

            html += `
            <div class="search-item">

                <div>

                    <b>${item.product}</b><br>

                    <small>${item.company}</small>

                </div>

                <div>

                    <a href="/brand/${item.company_url}">
                    View Company
                    </a>

                </div>

            </div>
            `;

        });

        searchResults.innerHTML = html;

    });

});

}



/* ==========================
   CLICK OUTSIDE
========================== */

document.addEventListener("click",function(e){

if(searchInput &&

!searchInput.contains(e.target) &&

!searchResults.contains(e.target)){

searchResults.innerHTML="";

}

});