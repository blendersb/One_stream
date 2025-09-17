var suggestions = document.querySelector('.suggestions');
var resultsContainer = document.getElementById('search');
var selected_id='';
var searchSuggest = "{{ url('searchquery') }}";
var search_page="{{ url('search')}}";
var nextPage_url="{{url('nextPage')}}"
var url = new URL(window.location.href);
let queryItem ='';
let nextPageToken = '{{nextPageToken}}';
let isFetching = false;
const params = new URLSearchParams(url.search);
if(params.get('q')){
  queryItem = params.get('q'); 
}else{
  queryItem='';
}
if (params.get('pageToken')){
  nextPageToken=params.get('pageToken');
}

  // Function to fetch more results
async function fetchMoreResults() {
    if (isFetching) return;
    isFetching = true;

    // Replace with the actual search query or parameter
    const response = await fetch(`${search_page}?q=${queryItem}}&pageToken=${nextPageToken}&type=json`);
    
    const data = await response.json();
    
    //console.log(data.data);
    
    // Process and append results
    
    if (data.data) {
        resultsContainer = document.getElementById('search');
        let list = JSON.parse(JSON.stringify(data.data));
        list.forEach(item => {
          //console.log(item);
            const videoDiv = document.createElement('div');
            videoDiv.classList.add("video-list","file-name");
            videoDiv.id=item.id.videoId;
            videoDiv.innerHTML = `
            <img class="video-img" alt="thumbnail" src="${item.snippet.thumbnails.default.url}" alt="${item.snippet.title}"/>
              <div width="70%">   
                <text class="video-title">${item.snippet.title}</text>
                <avatar>SV</avatar>
                <text class="video-channel" >${item.snippet.channelTitle}</text>
              </div>
            `;
            resultsContainer.appendChild(videoDiv);
            main();
        });
        nextPageToken = data.nextPageToken || '';
    }

    isFetching = false;
}

// Infinite scroll listener
window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
        fetchMoreResults();
    }
});

document.getElementById('searchBox').addEventListener('input', function() {
          let query = this.value;
          
          //console.log(url);
          if (query.length > 0) {
            suggestions.style.display = 'block';
              fetch(`${searchSuggest}?q=${query}`)
                  .then(response => response.json())
                  .then(data => {
                      //const resultsDiv = document.getElementById('autocompleteResults');
                      suggestions.innerHTML = '';
                      data[1].forEach(item => {
                          const div = document.createElement('li');
                          //div.classList.add('autocomplete-suggestion');
                          div.textContent = item;
                          div.addEventListener('click', () => {
                              document.getElementById('searchBox').value = item;
                              suggestions.innerHTML = '';
                              queryItem=item;
                              window.location.href = `${search_page}?q=${item}`;
                          });
                          suggestions.appendChild(div);
                      });
                  });
          }
          else if(query===''){
            suggestions.innerHTML='';
            suggestions.style.display = 'none';
            

          }
           else {
              document.getElementById('suggestions').innerHTML = '';
              suggestions.style.display = 'none';
          }
      });


//document.addEventListener('DOMContentLoaded', () => {
  
  
  
  function activateMainButton(){
    if (selected_id==''){
    window.Telegram.WebApp.MainButton.setText('Please Select to Play');
  }
  else{
    window.Telegram.WebApp.MainButton.setText('Play Now');
    window.Telegram.WebApp.MainButton.enable();
  }
  window.Telegram.WebApp.MainButton.show();
  }
  function onMainButtonClick() {
    
        const data = JSON.stringify(selected_id);
        window.Telegram.WebApp.sendData(data);
     
    
  }
function main(){  
  const selectableDivs = document.querySelectorAll('.file-name');
  window.Telegram.WebApp.ready();
  activateMainButton();
  selectableDivs.forEach(div => {
      div.removeEventListener('click',()=>{console.log('')})
      div.addEventListener('click', () => {
          // Remove the 'selected' class from all divs
          selectableDivs.forEach(d => d.classList.remove('selected'));

          // Add 'selected' class to the clicked div
          div.classList.add('selected');
          activateMainButton();
          window.Telegram.WebApp.expand();
          selected_id=div.id;
          // Get and print the ID of the selected div
          console.log('Selected div ID:', div.id);
      });
  });
  
  window.Telegram.WebApp.onEvent('mainButtonClicked', onMainButtonClick);
}
document.addEventListener('click', (event) => {
    if (!event.target.closest('.search_section')) {
        suggestions.style.display = 'none';
    }
});
main();
//});




