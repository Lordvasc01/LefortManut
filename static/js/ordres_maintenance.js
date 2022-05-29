$(document).ready(function(){
    // ***********Affiche les om clos*********
    if(localStorage.getItem('om_clos')=='true'){
        $('#om_clos').prop('checked',true)
        //$('tr[data-status="clos"]').show()
   
    }else{

        $('#om_clos').prop('checked',false)
        //$('tr[data-status="clos"]').hide()

    }

    $('body').on('click','#om_clos', function(){

        if($(this).prop('checked')==true){

            //$('tr[data-status="clos"]').show()
            localStorage.setItem('om_clos',true)
        
        }else{
            //$('tr[data-status="clos"]').hide()
            localStorage.setItem('om_clos',false)
        }
    })
    console.log('om_clos',localStorage.getItem('om_clos'))

    
    // ***********Affiche les om préventif*********
    if(localStorage.getItem('om_origine')=='true'){
        $('#om_curatif').prop('checked',true)
     
    }else{

        $('#om_curatif').prop('checked',false)
    
    }
  

    $('body').on('click','#om_curatif', function(){

        if($(this).prop('checked')){

            //$('tr[data-origine="preventif"]').show()
            localStorage.setItem('om_origine',true)
        }else{
            //$('tr[data-origine="preventif"]').hide()
            localStorage.setItem('om_origine',false)
        }
        
    })
    console.log('om_origin',localStorage.getItem('om_origine'))

    // ***********Affiche les om si*********
    if(localStorage.getItem('om_si')=='true'){
        $('#om_si').prop('checked',true)
       
    }else{

        $('#om_si').prop('checked',false)
        //$('tr[data-intervention="true"]').show()
    }
  

    $('body').on('click','#om_si', function(){

        if($(this).prop('checked')){

         
            localStorage.setItem('om_si',true)
        }else{
            //$('tr[data-intervention="true"]').show()
            localStorage.setItem('om_si',false)
        }
        
    })

    $('body').on('click','input[type="checkbox"]', function(e){

        
    })

    // toggle barre de filtre
    $('body').on('click','#show-filter', function(e){
        $('#filter').toggle()
    })

    $('#raz_dd').click(function(){
        $('#date_depart').val('')
    })
    $('#raz_df').click(function(){
        $('#date_fin').val('')
    })
})