const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');


const app = express();
const port = 3001;

// Cross Origin Resource Sharing, the client is probably running on a different domain
const cors = require('cors');

app.use(cors({
    origin: 'http://localhost:3000',
    methods: 'GET,POST,PUT,DELETE',
}));


app.use(express.json());

const csv = require('csv-parser');



var services = {};
var ids = {};
var rules = {};
var flags = [];





// Function that runs on startup
async function startupFunction() {
    console.log('Running startup function...');

    // Execute the Python script
    exec('python setup.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`Python script error: ${stderr}`);
            return;
        }

        console.log(`Python script output: ${stdout}`);

        fs.readFile('ids.json', 'utf8', (err, data) => {
            if (err) {
                console.error(`Error reading JSON file: ${err.message}`);
                return;
            }
            
            try {
                services = JSON.parse(data);

            } catch (err) {
                console.error(`Error parsing JSON: ${err.message}`);
                return;
            }
      

        fs.readFile('services.json', 'utf8', (err, data) => {
            if (err) {
                console.error(`Error reading JSON file: ${err.message}`);
                return;
            }
            
            try {
                ids = JSON.parse(data);
                console.log("IDs Within", ids);

            } catch (err) {
                console.error(`Error parsing JSON: ${err.message}`);
                return;
            }
        


        if (!fs.existsSync('rules.json')){
            fs.writeFile('rules.json', '{}', (err) => {
                if (err) {
                    console.error(`Error writing JSON file: ${err.message}`);
                    return;
                }
            });
        }

            var initialData = {
                global: []
            };
            
            // Create the file again and write the initial data as JSON
            console.log("IDs ", ids);
            for (const id in ids){
                
                initialData[id] =  [];
                flags[services[id]] = [];
                

                console.log(id);
    
            }
            console.log(initialData);
    
            fs.writeFile('rules.json', JSON.stringify(initialData), (err) => {
                if (err) {
                    console.error(`Error writing JSON file: ${err.message}`);
                    return;
                }
            });

        });
    });

    });
      
   
}


startupFunction(); // Call the startup function


app.get('/getServices', (req, res) => {
    res.send(services);
});

app.get("/getFlags", (req, res) => {
    res.send(flags);
});



app.post('/getData', (req, res) => {
    const id = req.body.id;
    console.log(id);
    var results = [];
    fs.createReadStream(`./runTimeData/${services[id]}/data.csv`)
  .pipe(csv())
  .on('data', (data) => results.push(data))
  .on('end', () => {
    //console.log(results);

    const lastResult = results[results.length - 1];

    const lastTime = new Date(lastResult.usage_end_time);

   // console.log(lastTime);
    const firstTime = new Date(lastTime.getTime() - (1000 * 60 * 60 *24 *4));
  //  console.log(firstTime);

    searching = true;
    let i = 0;
    let sendData = [];
    let datapts = 0;

    results.reverse();
    sendData[i] = results[i];
    //console.log("END TIME", (new Date(results[i].usage_end_time).getTime()-firstTime));
    sendData[i].usage_end_time = new Date(results[i].usage_end_time).getTime()-firstTime;
    while(searching){

        const time = new Date(results[i].usage_end_time).getTime();
        const time2 = new Date(results[i+1].usage_end_time).getTime()-firstTime;
       // console.log(time, "==",time2);

        if (time == time2){
            sendData[i].cost = parseFloat(sendData[i].cost) + parseFloat(results[i+1].cost);
            sendData[i].usage_amount = parseFloat(sendData[i].usage_amount) + parseFloat(results[i+1].usage_amount);


            results.splice(i+1, 1);

        }else{

            i++;
            sendData[i] = results[i];
            sendData[i].usage_end_time = (new Date(results[i].usage_end_time).getTime())-firstTime;

        }

        if(i == results.length-1){
            console.log("End of data");
            searching = false;
        }
        else if (sendData[i].usage_end_time<= 0){
            console.log("4 days exceeded")
            searching = false;
        }else if (i >= 50){
            searching = false;
            console.log("10000 datapoints reached");

        }
       
        
    }
   // console.log(results);
 //  sendData[0].usage_end_time = 0;
    const sendFinal = (sendData.slice(0, i)).reverse();
    console.log(sendFinal);
    res.send(sendFinal);

    // You can process your CSV data here
  });

});

app.post('/getRules', (req, res) => {
    

    const id = req.body.id;

    res.send(rules[id]);

});

app.post('/updateRules', (req, res) => {    
    const id = req.body.id;
    const rules = req.body.rules;

    rules[id] = rules;

    fs.writeFile('rules.json', JSON.stringify(rules), (err) => {
        if (err) {
            console.error(`Error writing JSON file: ${err.message}`);
            return;
        }
    });

});


app.get('/', (req, res) => {
    res.send('Hello, world!');
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
