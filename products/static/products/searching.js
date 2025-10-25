const url = window.location.href
const searchForm = document.getElementById('search-form')
const searchInput = document.getElementById('search-input')
const resultsBox = document.getElementById('live-results')

const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

window.getSearchInput = function() {
  return document.getElementById('search-input');
};

window.getResultsBox = function() {
    return document.getElementById('live-results')
};



const sendSearchData = (game) => {
    $.ajax({
        type:"POST",
        url: '/products/search2/',
        data:{
            'csrfmiddlewaretoken':csrf,
            'game': game
        },
        success: (res)=>{
            resultsBox.innerHTML = '';
            console.log(res.data)
            const data = res.data
            if (Array.isArray(data)){
                data.forEach(game=> {
                    resultsBox.innerHTML += `
                        <a href="" class="item">
                            <div class="row mt-2 mb-2">
                               <div class="col-10">
                                    <h5>${game.product_name}</h5>
                               </div>
                            </div>

                        </a>
                    `
                })
            }
            else {
                if (searchInput.value.length > 0){
                    resultsBox.innerHtml = `<b>${data}</b>`
                }
                else{
                    resultsBox.classList.add('not-visible')
                }

            }

        },
        error: (err) =>{
            console.log(err)
        }
    })

}


searchInput.addEventListener('keyup', e=>{
    console.log(e.target.value)

    if (resultsBox.classList.contains('not-visible')){
        resultsBox.classList.remove('not-visible')
    }

    sendSearchData(e.target.value)
})
