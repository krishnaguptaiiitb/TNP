import { useState, useEffect, useRef } from "react";
import ListIcon from "../assets/list.svg";
import GridIcon from "../assets/grid.svg";
import "./students.css";
const BASE_URL = import.meta.env.VITE_API_BASE_URL;
const STUDENT_BASE = `${BASE_URL}/api/students`;
const allFields = {
    name: "Name",
    scholar_no: "Scholar No",
    program: "Program",
    graduation_year: "Year",
    mail_id: "Email",
    phone_no: "Phone",
    placement_active: "Placement Status",
    internship_active: "Internship Status",
  };


const FieldSelector = ({exportFunction, initialList}) => {

  const [selected, setSelected] = useState(initialList || []);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const dragItem = useRef(null);
  const dragOverItem = useRef(null);

  const remainingFields = Object.keys(allFields).filter(
    (k) => !selected.includes(k)
  );

  const handleAdd = (key) => {
    setSelected([...selected, key]);
    setShowDropdown(false);
  };

  const handleRemove = (key) => {
    setSelected(selected.filter((item) => item !== key));
  };

  // Drag handlers
  const handleDragStart = (index) => {
    dragItem.current = index;
  };

  const handleDragEnter = (index) => {
    dragOverItem.current = index;
  };

  const handleDragEnd = () => {
    const newList = [...selected];
    const draggedItem = newList.splice(dragItem.current, 1)[0];
    newList.splice(dragOverItem.current, 0, draggedItem);
    dragItem.current = null;
    dragOverItem.current = null;
    setSelected(newList);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  useEffect(() => {
    if (exportFunction) {
      exportFunction(selected);
    }
    }, [selected]);

  return (
    <div className="field-selector" ref={dropdownRef}>
      <div className="selected-tags">
        {selected.map((key, index) => (
          <div
            className="tag"
            key={key}
            draggable
            onDragStart={() => handleDragStart(index)}
            onDragEnter={() => handleDragEnter(index)}
            onDragEnd={handleDragEnd}
            title="Drag to reorder"
          >
            <span>{allFields[key]}</span>
            <button
              className="remove-btn"
              onClick={() => handleRemove(key)}
              title="Remove"
            >
              &times;
            </button>
          </div>
        ))}
      </div>

      {remainingFields.length > 0 && (
        <button
          className="add-field-btn"
          onClick={() => setShowDropdown(!showDropdown)}
          title="Add Field"
        >
          +
        </button>
      )}

      {showDropdown && remainingFields.length > 0 && (
        <div className="dropdown">
          {remainingFields.map((key) => (
            <div
              key={key}
              className="dropdown-item"
              onClick={() => handleAdd(key)}
            >
              {allFields[key]}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


const ViewCard = ({ studentList, viewType, fieldList}) => {

    if (!studentList || studentList.length === 0) {
        return <div>No information Available</div>;
    }

    console.log("view type : ", viewType);

    const available_fields = {
        "name" : (k) => (k.name),
        "scholar_no" : (k) => (k.scholar_no),
        "placement_active" : (k) => (k.placement_active),
        "internship_active" : (k) => (k.internship_active),
        "phone_no" : (k) => (k.phone_no),
        "program" : (k) => (k.program),
        "mail_id" : (k) => (k.mail_id),
        "graduation_year" : (k) => (new Date(k.graduation_year).getFullYear()),
    }

    return (
        <>
            { viewType === "list" && (
                <div>
                   <table>
                    <thead>
                        <tr>
                            <th>Index</th>
                            {
                                fieldList.map((field_name, idx)=>(
                                    <th key={`${field_name}-${idx}`}>{allFields[field_name]}</th>
                                ))
                            }
                        </tr>
                    </thead>
                    <tbody>
                        {studentList.data.map((student, idx) => (
                            <tr key={student.scholar_no}>
                                <td>{idx + 1}</td>
                                {fieldList.map((field_name, fidx) => (
                                    <td key={`${student.scholar_no}-${field_name}-${fidx}`}>
                                        {available_fields[field_name](student)}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                   </table>
                </div>
            )}

            { viewType === "grid"  && (
                <div>
                    grid content
                </div>
            )}
        </>
    );
}

export default ()=>{
    const initialList = ['scholar_no', 'name', 'program', 'graduation_year', 'placement_active'];
    const viewList = {"list" : ListIcon, "grid" : GridIcon};
    const [studentListObject, setStudentListObject] = useState([]);
    const [selectedFields, setSelectedFields] = useState(initialList);
    const [viewType, setViewType] = useState(0);
    const fetchStudents = async () => {
        try {
            const response = await fetch(`${STUDENT_BASE}/list`);
            const data = await response.json();
            console.log(data);
            setStudentListObject(data);
        } catch (error) {
            console.error("Error fetching students:", error);
        }
    };

    useEffect(() => {
        console.log(fetchStudents());
    }, []);


    return (
        <>
            <h1> Student Panel </h1>
            <FieldSelector exportFunction={setSelectedFields} initialList={initialList}/>
            <button onClick={() => setViewType((viewType)=>(viewType^1))}>
                <img src={Object.entries(viewList)[viewType][1]} alt="" style={{width:"30px", height:"30px"}}/>
            </button>
            <ViewCard studentList={studentListObject} viewType={Object.entries(viewList)[viewType][0]} fieldList={selectedFields}/>
        </>
    );
    
}