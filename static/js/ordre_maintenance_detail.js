$(document).ready(function(){
$('body').on('click','#show_outils', function(){

    if($('#outils').hasClass('d-none')){
        $('#outils').removeClass('d-none')
        $(this).text('Masquer les outils spécifiques')
    }else{
    $('#outils').addClass('d-none')
     $(this).text('Afficher les outils spécifiques')
    }
})

})