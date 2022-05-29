$(document).ready(function(){
    $('body').on('keyup','#search_materiel', function(e){
        if (e.target.value.length >1){
        var xhr = new XMLHttpRequest()
        xhr.open('post','http://'+window.location.host+'/api/materiel/get', true)

        xhr.responseType = 'json'
        xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded")
        data = 'data='+e.target.value
        xhr.onload = function(){
        var data = '<ul class="card bg-light text-center">'
        this.response.forEach(element => {
            data = data+'<li class="btn btn-sm  text-start" data-item="'+element.id+'">Client: '+element.client+' '+element.ville+' Matériel: '+element.marque+' '+element.modele+' N°série: '+element.numero_serie+'</li>'

        })
        data = data +'</ul>'
        $('#resultat_search').html(data)

        }
        xhr.send(data)
        }

    })
    $('body').on('click','#resultat_search>ul>li',function(e){
             $('#materiel_id option[value='+$(e.target).data('item')+']').prop('selected', true)
             $('#resultat_search').hide()
             $('#search_materiel').hide()
             var data = $(e.target).text().split(' Matériel: ')

             $('#client').text(data[0]);
             $('#materiel_data').text(data[1]);
             $('#search_materiel').val($(e.target).text());
             $('#display').show()

            })
    $('body').on('click','#raz_search', function(){
        $('#search_materiel').val('')
        $('#search_materiel').show()
        $('#display').hide()
        $('#resultat_search').html('')
        $('#resultat_search').show()

    })
    $('body').click(function(){
        $('#resultat_search').html('')

    })

})