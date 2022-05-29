$(document).ready(function(){

    $('body').on('keyup', '#marque', function(e){
        if(e.target.value.length>0){
            var xhr = new XMLHttpRequest()
            var data = 'data='+e.target.value
            xhr.open('post','http://'+window.location.host+'/api/materiel_type/get', true)
            xhr.responseType = 'json'
            xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded")
            xhr.onload = function(){
                var data_response = []
                if (this.response.length>0){
                    this.response.forEach(element => {
                        if(! data_response.includes('<div>'+element.marque+'</div>')){
                            data_response.push('<div>'+element.marque+'</div>')
                            }
                        });

                        console.log(data_response)
                        $('#resultat-marque').html(data_response)
                        $('#resultat-marque').show()

                        $('body').on('click','#resultat-marque>div', function(e){
                            
                            $('#marque').val(e.target.innerText);
                            $('#resultat-marque').html('');
                            $('#resultat-marque').hide()
                            
                        })
                        $('body').click(function(){
                            $('#resultat-marque').hide()
                        })
                }else{
                    $('#resultat-marque').html('')
                    $('#resultat-marque').hide()
                }
                }
               
            xhr.send(data)}
        else{
            $('#resultat-marque').html('')
            $('#resultat-marque').hide()}
    })

    $('body').on('keyup', '#categorie', function(e){
        if(e.target.value.length>0){
            var xhr = new XMLHttpRequest()
            var data = 'data='+e.target.value
            xhr.open('post','http://'+window.location.host+'/api/materiel_type/categorie/get', true)
            xhr.responseType = 'json'
            xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded")
            xhr.onload = function(){
                var data_response = []
                if (this.response.length>0){
                    this.response.forEach(element => {
                        if(! data_response.includes('<div>'+element.categorie+'</div>')){
                            data_response.push('<div>'+element.categorie+'</div>')
                            }
                        });

                        console.log(data_response)
                        $('#resultat-categorie').html(data_response)
                        $('#resultat-categorie').show()

                        $('body').on('click','#resultat-categorie>div', function(e){
                            
                            $('#categorie').val(e.target.innerText);
                            $('#resultat-categorie').html('');
                            $('#resultat-categorie').hide()
                            
                        })
                        $('body').click(function(){
                            $('#resultat-categorie').hide()
                        })
                }else{
                    $('#resultat-categorie').html('')
                    $('#resultat-categorie').hide()
                }
                }
               
            xhr.send(data)}
        else{
            $('#resultat-categorie').html('')
            $('#resultat-categorie').hide()}
    })

    $('body').on('click','#list_categorie',function(){
        var xhr = new XMLHttpRequest();
        xhr.open('get', 'http://'+window.location.host+'/api/materiel_type/categories');
        xhr.responseType = 'json';
        var tab = []
        xhr.onload = function(){
            this.response.forEach(element => {
                tab.push('<li>'+element+'</li>')
            });
            $('#resultat-categorie').html(tab)
            $('#resultat-categorie').show()
            $('#resultat-categorie>li').click(function(e){

                $('#categorie').val(e.target.innerText)
                $('#resultat-categorie').hide()
            })
        }
        xhr.send()
    })

    $('body').on('click','#list_marque',function(){
        var xhr = new XMLHttpRequest();
        xhr.open('get', 'http://'+window.location.host+'/api/materiel_type/marques');
        xhr.responseType = 'json';
        var tab = []
        xhr.onload = function(){
            this.response.forEach(element => {
                tab.push('<li>'+element+'</li>')
            });
            $('#resultat-marque').html(tab)
            $('#resultat-marque').show()
            $('#resultat-marque>li').click(function(e){

                $('#marque').val(e.target.innerText)
                $('#resultat-marque').hide()
            })
        }
        xhr.send()
    })

    $('body').click(function(){
        $('#resultat-categorie').hide()
        $('#resultat-marque').hide()
    })

    // affiche la liste des composants
    $('body').on('click','#show_composant', function(e){

        $('#sousensembles').toggle()
    })

    // affiche la liste des gammes
    $('body').on('click','#show_gamme', function(e){

        $('#gammes').toggle()
    })

})