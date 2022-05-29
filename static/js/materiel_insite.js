$(document).ready(function(){

$('#see_material').click(function(e){
    e.stopPropagation()
    $('#materieltype_id').toggle()
    $('#resultat-row').hide()
})


$('body').on('keyup', '#search_materieltype', function(e){
    var value = e.target.value;
    $('input[name="materieltype_id"]:checked').prop('checked','')

    if(value.length >1){
        var xml = new XMLHttpRequest()
        var host = window.location.host
        var data = "data="+e.target.value
        xml.open('post','http://'+host+'/api/materiel_type/get', true);
        xml.responseType = 'json'
        xml.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        xml.onload = function(){
            
            if(this.response.length>0){
                $('#resultat-row').show()
                $('#resultat-materieltype').show()
                var data='';
                this.response.forEach(element => {
                    data = data+'<li style="list-style:none" id="mat-'+element.id+'">'+element.marque+' '+element.modele+' '+element.categorie+'</li>';
                });
          
                $('#resultat-materieltype').html(data)

                $('body').on('click','#resultat-materieltype>li', function(e){
                    var id = e.target.id.split('-')[1]
                    var nom = e.target.innerText
                    var input = $('input[value='+id+']')
                    $(input).prop('checked',true)
                    $('#resultat-row').hide()
                    $('#resultat-materieltype').hide()
                    $('#search_materieltype').val(nom)
                })
            }
        }

        xml.send(data)
    }else{
        $('#resultat-row').hide()
    }



})
$('body').on('click', '#materieltype_id>li>input', function(e){
    e.stopPropagation()
    $('#materieltype_id').hide()
    $('#search_materieltype').val($(e.target).next().text())
})
$('body').click(function(){
    $('#materieltype_id').hide()
    $('#resultat-row').hide()
    var tab = $('input[name="materieltype_id"]:checked')
    if(!tab.length>0){
        $('#search_materieltype').val('')
    }

})

})

