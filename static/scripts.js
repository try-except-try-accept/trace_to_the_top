


function check_inputs_provided()
{
    if (document.getElementById("inputs").value === "" && document.getElementById("code_submit").value.indexOf("input") > -1)
    {
        alert("Looks like you need to provide some inputs...")
        return false;
    }
    return true;
}