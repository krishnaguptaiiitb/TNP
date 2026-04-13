import { useState } from 'react'
import coverImg from '../assets/cover.jpg'
export default ({data, setShowInfo})=>{
    
    return (

        <div className="company-card">

            <img src={coverImg} />
            <div className='company-card-text'>
                <span style={{fontWeight: "bolder"}}>{data.company_name}</span>
                <span>{data.job_type} | {data.location}</span>
                <span>{`Applied ${data.applied_students}`} | {`Selected ${data.selected_students}`}</span>
                <div className="btn-grp">
                    <button className='company-btn'> Add </button>
                    <button className='company-btn' onClick={()=>setShowInfo(data)}> Info </button>
                </div>
            </div>
            
        </div>
    )
}