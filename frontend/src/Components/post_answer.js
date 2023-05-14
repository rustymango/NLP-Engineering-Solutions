import axios from 'axios';
import React, { Component, useState, useEffect } from 'react';
// import { useParams } from 'react-router-dom';

function PostCalculations () {

    var postFromResponse = null;
    const [calculations, setCalculations] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    function fetchCalculations () {

    setLoading(true);
    axios
    
        .get("http://127.0.0.1:5000/calculations")
        .then(response => response.data)
        .then((data) => {
            setCalculations(data.calculations)
            console.log(data)

        })
        .catch((error) => {
            setError(error.message);
        })
        .finally(() => {
            setLoading(false);
        })
    }

    useEffect(() => {
        fetchCalculations();
    }, [])


    const table = {
        margin: '0 auto',
        padding: '0px 0px 5px 0px',
        width: '80%'
    }

    const td ={
        padding: '0px 0px 20px 0px',
        textAlign: 'center'
    }

    if (calculations?.length > 0) {
        console.log(calculations?.length)
        return(
            <div>
                <h2>Calculation Results:</h2>
                {/* <table style={table}>
                    <thead>
                        <tr>
                        <th>Calculation Steps:</th>
                        <th>Answer:</th>
                        </tr>
                    </thead>
                    <tbody>
                        {calculations.map((calculation) => (
                        <React.Fragment key={calculation.id}>
                            <tr>
                            <td style={td}>{calculation.formula_1}</td>
                            <td rowSpan="5" style={{ ...td, verticalAlign: "middle" }}>
                                {calculation.answer}
                            </td>
                            </tr>
                            <tr>
                            <td style={{ ...td, paddingTop: "0.2em" }}>{calculation.values_1}</td>
                            </tr>
                            <tr>
                            <td style={{ ...td, paddingBottom: "0.2em" }}>{calculation.formula_2}</td>
                            </tr>
                            <tr>
                            <td style={{ ...td, paddingTop: "0.2em" }}>{calculation.values_2}</td>
                            </tr>
                            <tr>
                            <td style={{ ...td, paddingBottom: "0.2em" }}>{calculation.formula_3}</td>
                            </tr>
                            <tr>
                            <td style={{ ...td, paddingTop: "0.2em" }}>{calculation.values_3}</td>
                            </tr>
                        </React.Fragment>
                        ))}
                    </tbody>
                    </table> */}
                <table style={table}>
                <thead>
                    <tr>
                    <th>Answer:</th>
                    </tr>
                </thead>
                <tbody>
                    {calculations.map((calculation) => (
                    <React.Fragment key={calculation.id}>
                        <tr>
                        <td style={{ ...td, paddingTop: "0.4em", paddingBottom: "2em" }}>{calculation.answer}</td>
                        </tr>
                        <th>Calculation Steps:</th>
                        <tr>
                        <td style={{ ...td, paddingTop: "0.5em" }}>
                            <div style={{ display: "flex", flexDirection: "column" }}>
                            <div style={td}>{calculation.formula_1}</div>
                            <div style={{ ...td, paddingTop: "0.2em" }}>{calculation.values_1}</div>
                            <div style={{ ...td, paddingBottom: "0.2em" }}>{calculation.formula_2}</div>
                            <div style={{ ...td, paddingTop: "0.2em" }}>{calculation.values_2}</div>
                            <div style={{ ...td, paddingBottom: "0.2em" }}>{calculation.formula_3}</div>
                            <div style={{ ...td, paddingTop: "0.2em" }}>{calculation.values_3}</div>
                            </div>
                        </td>
                        </tr>
                    </React.Fragment>
                    ))}
                </tbody>
                </table>
            </div>
        )
    }
    else {
        console.log(calculations?.length)
        return(
            <div>
                <h3>Please enter a problem above!</h3>
            </div>
        )
    }

};

export default PostCalculations