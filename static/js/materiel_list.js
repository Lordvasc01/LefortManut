$(document).ready(function(){
    $('body').on('keyup','#search_materiel', function(e){
        if (e.target.value.length >1){
        var xhr = new XMLHttpRequest()
        xhr.open('post','http://'+window.location.host+'/api/materiel/get', true)

        xhr.responseType = 'json'
        xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded")
        data = 'data='+e.target.value
        xhr.onload = function(){
        var data=''
        if(this.response.length>0){
            data = '<ul class="card bg-light text-center pt-1 pb-3">'
            this.response.forEach(element => {
            data = data+'<li class="text-start" data-item="'+element.id+'"><a class="btn btn-sm" style="text-decoration:none; color:black" href="http://'+window.location.host+'/materielinsite/detail/'+element.id+'" >Client: '+element.client+' '+element.ville+' Matériel: '+element.marque+' '+element.modele+' N°série: '+element.numero_serie+'</a></li>'
            })
        data = data +'</ul>'

        }

        $('#resultat_search').html(data)

        }
        xhr.send(data)
        }

    })


        $('body').on('click','#resultat_search>ul>li',function(e){
            e.stopPropagation();
             $('#resultat_search').text('')
             $('#search_materiel').val($(e.target).text());
            })
        $('body').on('click','#raz_search', function(){
        $('#search_materiel').val('');
        $('#resultat_search').text('');
        })

        $('body').on('click',function(){
            $('#search_materiel').val('');
            $('#resultat_search').text('');
        })
    })