$(document).ready(function(){
  //adds an additional file when the add button is presses
  $("[name=add]").click(function(){
    numFiles = parseInt($(this).attr("num-files"))
    if(numFiles < max_files) {
      input='<div class="form-group"><label class="col-sm-2" for="additional-'+ numFiles +'">Additonal File</label><input class="col-sm-3" name="additional-' + numFiles + '"type="file"></div>';
      $(input).insertBefore($(this).parent().parent());
      $(this).attr("num-files",numFiles+1);
    }
  });
});

$('#soln_form').submit(function () {
  returnval = true
  $("input[type=file]").each(function(index, element){
    if (element.value === '') {
      alert('You forgot to upload a file!');
      returnval = false;
      //this resturn statement makes the function stop after one unsubmitted file
      return false;
    }
  });
  //and this return statement makes the form not submit
  return returnval
});
