function transform(line) {
    var values = line.split(',');
    var obj = new Object();
    obj.Year = values[0].replace(/"/g, '');
    obj.Total_IT_Job_Openings = parseInt(values[1].replace(/"/g, ''));
    obj.Web_Related_Jobs = parseInt(values[2].replace(/"/g, ''));
    obj.Software_Development_Jobs = parseInt(values[3].replace(/"/g, ''));
    obj.IT_Support_Jobs = parseInt(values[4].replace(/"/g, ''));
    obj.IT_Management_Jobs = parseInt(values[5].replace(/"/g, ''));
    obj.IT_Security_Jobs = parseInt(values[6].replace(/"/g, ''));
    obj.Hardware_Engineering_Jobs = parseInt(values[7].replace(/"/g, ''));
    obj.Impacting_Event = values[8];
    obj.Job_Loss_Percentage_Due_to_Event = values[9];
    obj.New_Emerging_IT_Roles = values[10];
    obj.prim = parseInt(values[11].replace(/"/g, ''));
    obj.Total_IT_Job_Openings_Mean = parseFloat(values[12].replace(/"/g, ''));
    var jsonString = JSON.stringify(obj);
    return jsonString;
}