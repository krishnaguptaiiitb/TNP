import { useEffect, useRef, useState } from "react";
import Company from './company';
import "./companies.css";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;
const COMPANY_CREATE_URL = `${BASE_URL}/api/placements/companies/`;
const COMPANY_UPDATE_URL = `${BASE_URL}/api/placements/companies`;
// Define the initial empty state for clarity and easy reuse
const initialFormData = {
    query: '',
    company_name: '',
    posts: '',
    job_type: '',
    ctc_min: '',
    ctc_max: '',
    visit_date: '',
    location: '',
    status: '',
    applied_students: 0,
    selected_students: 0
};


const initialFilterState = {
    company_name: '',
    visit_date_min: '',
    visit_date_max: '',
    applied_students_min: '',
    applied_students_max: '',
    selected_students_min: '',
    selected_students_max: '',
    job_type: '',
    status: '',
    ctc_min: '',
    ctc_max: '',
};


const objectToQueryString = (paramsObj) => {
    const params = new URLSearchParams();

    // Iterate over all keys in the object
    for (const key in paramsObj) {
        if (paramsObj.hasOwnProperty(key)) {
            const value = paramsObj[key];

            // 1. Check for valid/non-empty values
            // We exclude '', null, undefined, and the number 0 (since it often means 'no filter')
            if (value !== '' && value !== null && value !== undefined) {
                
                // 2. Handle specific exclusion for the number 0 if it's not explicitly desired
                // This logic ensures that if the value is explicitly the number 0, it is also skipped.
                // You can remove the 'value !== 0' part if you *do* want 'key=0' in the URL.
                if (typeof value === 'number' && value === 0) {
                    continue; // Skip the number zero
                }
                
                // 3. Append the key-value pair, converting the value to a string
                params.set(key, String(value));
            }
        }
    }

    // Return the generated string, prepended with a '?'
    const queryString = params.toString();
    return queryString ? `?${queryString}` : '';
};

const CompanyFilter = ({ oldFilter, onApplyFilter, showSet }) => {
    const [filters, setFilters] = useState(oldFilter);
    const [showAdvanced, setShowAdvanced] = useState(false); // State to toggle advanced filters

    // Dropdown options (using the same options defined in EditableInfo)
    const dropdownOptions = {
        job_type: ['Full_Time', 'Internship', 'Both'],
        status: ['Upcoming', 'Visited', 'Rejected', 'Pending']
    };

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));

        console.log(filters);
    };

    const handleApply = (e) => {
        e.preventDefault();
        // Pass the cleaned filter object back to the parent component
        // const cleanedFilters = Object.fromEntries(
            // Object.entries(filters).filter(([_, value]) => value !== '' && value !== null)
        // );
        onApplyFilter(filters);
        showSet(false); // Optionally close the filter modal on apply
    };

    const handleClear = () => {
        // setFilters(initialFilterState);
        onApplyFilter(initialFilterState); // Send an empty object to clear all filters in the parent
    };

    return (
        <div className="filter-modal-overlay">
            <div className="company-filter-container">
                <form onSubmit={handleApply}>
                    <div className='form-field header-field'>
                        <h2>Filter Companies</h2>
                        <button type="button" className="close-btn" onClick={()=>showSet(false)}> &times; </button>
                    </div>

                    <div className="filter-grid">
                        {/* 1. Company Name */}
                        <div className='filter-field'>
                            <label htmlFor='company_name'>Company Name (Search)</label>
                            <input 
                                id="company_name" 
                                name="company_name" 
                                value={filters.company_name} 
                                onChange={handleFilterChange} 
                                placeholder='e.g., Google'
                            />
                        </div>

                        {/* 2. Job Type Dropdown */}
                        <div className='filter-field'>
                            <label htmlFor='job_type'>Job Type</label>
                            <select 
                                id="job_type" 
                                name="job_type" 
                                value={filters.job_type} 
                                onChange={handleFilterChange}
                            >
                                <option value={''}>All Job Types</option>
                                {dropdownOptions.job_type.map(opt => (
                                    <option key={opt} value={opt}>{opt.replace('_', ' ')}</option>
                                ))}
                            </select>
                        </div>

                        {/* 3. Job Status Dropdown */}
                        <div className='filter-field'>
                            <label htmlFor='status'>Job Status</label>
                            <select 
                                id="status" 
                                name="status" 
                                value={filters.status} 
                                onChange={handleFilterChange}
                            >
                                <option value={''}>All Statuses</option>
                                {dropdownOptions.status.map(opt => (
                                    <option key={opt} value={opt}>{opt}</option>
                                ))}
                            </select>
                        </div>
                        
                        {/* 4. CTC Min/Max Range */}
                        <div className='filter-field range-group'>
                            <label>CTC Value (LPA)</label>
                            <div className='range-inputs'>
                                <input id="ctc_min" name="ctc_min" type="number" placeholder="Min" 
                                    value={filters.ctc_min} onChange={handleFilterChange} />
                                <input id="ctc_max" name="ctc_max" type="number" placeholder="Max" 
                                    value={filters.ctc_max} onChange={handleFilterChange} />
                            </div>
                        </div>

                        {/* --- Advanced Filters Toggle --- */}
                        <button 
                            type="button" 
                            className="advanced-toggle-btn"
                            onClick={() => setShowAdvanced(prev => !prev)}
                        >
                            {showAdvanced ? 'Hide Advanced Filters ▲' : 'Show Advanced Filters ▼'}
                        </button>
                    </div>

                    {/* --- ADVANCED FILTER SECTION --- */}
                    {showAdvanced && (
                        <div className="filter-grid advanced-filters-grid">
                            
                            {/* 5. Visit Date Range */}
                            <div className='filter-field range-group'>
                                <label>Visit Date Range</label>
                                <div className='range-inputs'>
                                    <input id="visit_date_min" name="visit_date_min" type="date" placeholder="From"
                                        value={filters.visit_date_min} onChange={handleFilterChange} />
                                    <input id="visit_date_max" name="visit_date_max" type="date" placeholder="To"
                                        value={filters.visit_date_max} onChange={handleFilterChange} />
                                </div>
                            </div>

                            {/* 6. Applied Students Range */}
                            <div className='filter-field range-group'>
                                <label>Applied Students Range</label>
                                <div className='range-inputs'>
                                    <input id="applied_students_min" name="applied_students_min" type="number" placeholder="Min"
                                        value={filters.applied_students_min} onChange={handleFilterChange} />
                                    <input id="applied_students_max" name="applied_students_max" type="number" placeholder="Max"
                                        value={filters.applied_students_max} onChange={handleFilterChange} />
                                </div>
                            </div>
                            
                            {/* 7. Selected Students Range */}
                            <div className='filter-field range-group'>
                                <label>Selected Students Range</label>
                                <div className='range-inputs'>
                                    <input id="selected_students_min" name="selected_students_min" type="number" placeholder="Min"
                                        value={filters.selected_students_min} onChange={handleFilterChange} />
                                    <input id="selected_students_max" name="selected_students_max" type="number" placeholder="Max"
                                        value={filters.selected_students_max} onChange={handleFilterChange} />
                                </div>
                            </div>
                            {/* Empty div for spacing in the grid */}
                            <div></div> 
                        </div>
                    )}
                    {/* --- END ADVANCED FILTER SECTION --- */}

                    {/* Action Buttons */}
                    <div className="filter-action-area">
                        <button type="button" className="clear-filter-btn" onClick={handleClear}>Clear Filters</button>
                        <button type="submit" className="apply-filter-btn">Apply Filters</button>
                    </div>
                </form>
            </div>
        </div>
    );
};



// --- Mock Notification/Toast Component (In a real app, this would be global) ---
const Notification = ({ message, type, onClose }) => {
    useEffect(() => {
        if (!message) return;
        const timer = setTimeout(onClose, 4000); // Auto-close after 4 seconds
        return () => clearTimeout(timer);
    }, [message, onClose]);

    if (!message) return null;

    const style = {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 25px',
        borderRadius: '5px',
        backgroundColor: type === 'success' ? '#4CAF50' : type === 'error' ? '#F44336' : '#2196F3',
        color: 'white',
        zIndex: 1000,
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
        transition: 'opacity 0.5s',
        opacity: message ? 1 : 0
    };

    return (
        <div style={style}>
            {message}
            <button onClick={onClose} style={{ marginLeft: '10px', background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontWeight: 'bold' }}>
                &times;
            </button>
        </div>
    );
};
// -------------------------------------------------------------------------------


// EditableInfo component from Companies.jsx
const EditableInfo = ({ data, setShowInfo, onDataSave, onUpdateSuccess }) => {
    // ... (Existing state and refs remain unchanged)
    const [formData, setFormData] = useState(data);
    const [editableField, setEditableField] = useState(null);
    const fieldRefs = useRef({});
    const wrapperRef = useRef(null);

    // Ensure COMPANY_UPDATE_URL and BASE_URL are accessible or passed down if needed, 
    // but we'll assume they're in the scope or passed via props for this solution.
    // For this demonstration, we'll assume they are available in the scope (as in the original file).
    const COMPANY_UPDATE_URL = `${BASE_URL}/api/placements/companies`;
    
    // Define the options for dropdowns here to reuse them
    const dropdownOptions = {
        job_type: ['Full_Time', 'Internship', 'Both'],
        location: ['Onsite', 'Remote', 'Hybrid'],
        status: ['Upcoming', 'Visited', 'Rejected', 'Pending']
    };

    const getActiveElement = () => fieldRefs.current[editableField];

    const setCursorToEnd = (element) => {
        if (window.getSelection && document.createRange) {
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(element);
            range.collapse(false);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    };

    // 2. EFFECT HOOK: Outside Click Handler
    useEffect(() => {
        const handleOutsideClick = (event) => {
            if (editableField) {
                if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                    const element = getActiveElement();
                    
                    if (element) {
                        // Check if it's a contentEditable span
                        if (element.getAttribute('contenteditable') === 'true') {
                            handleSave(element.textContent);
                        } 
                        // It's a select or input[type=date], save its value
                        else if (element.tagName === 'SELECT' || element.type === 'date') {
                            handleSave(element.value);
                        }
                    }
                }
            }
        };

        document.addEventListener('mousedown', handleOutsideClick);
        return () => {
            document.removeEventListener('mousedown', handleOutsideClick);
        };
    }, [editableField]); 

    // 3. HANDLERS

    // Generic handler to manage saving (updates local state)
    const handleSave = (newValue) => {
        if (!editableField) return;

        const key = editableField;
        
        if (String(formData[key]) !== String(newValue)) {
            const updatedData = { ...formData, [key]: newValue };
            setFormData(updatedData);
            
            // Note: Individual field API call (PATCH) is currently commented out, 
            // the main save is done on final submit (PUT)
        }
        
        setEditableField(null); // Exit editing mode
    };

    // Handler for the "edit" button click
    const handleEditClick = (fieldName) => {
        setEditableField(fieldName);
        
        setTimeout(() => {
            const element = fieldRefs.current[fieldName];
            if (element) {
                element.focus();
                
                // Only set cursor for contentEditable spans
                if (element.getAttribute('contenteditable') === 'true') {
                    setCursorToEnd(element);
                }
            }
        }, 0);
    };
    
    // Handler for the "View" button
    const handleViewClick = (fieldName) => {
        alert(`Viewing student list for: ${fieldName.replace('_', ' ')} (${formData[fieldName]})`);
        console.log(`Action: View ${fieldName} for company ID ${formData.company_id || 'N/A'}`);
    };
    
    // Handler for contentEditable onBlur event
    const handleBlur = (event) => {
        handleSave(event.target.textContent);
    };

    // Handler for Enter key press on contentEditable fields
    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            event.target.blur(); // Trigger handleBlur/handleSave
        }
    };

    // Handler for standard <input> or <select> changes
    const handleInputChange = (event) => {
        const { value } = event.target;
        // Update state immediately upon change for standard inputs/selects
        setFormData(prev => ({ ...prev, [editableField]: value }));
        
        // Save and exit editing mode instantly for non-contentEditable fields
        handleSave(value); 
    };

    // 🔑 UPDATED FINAL FORM SUBMISSION HANDLER WITH PUT REQUEST
    const handleFinalSubmit = async (e) => {
        e.preventDefault();
        
        // Ensure there's an ID for the update
        if (!formData.company_id) {
            console.error("Cannot update company: ID is missing.");
            onUpdateSuccess({ message: '❌ Error: Company ID missing for update.', type: 'error' });
            return;
        }

        const url = `${COMPANY_UPDATE_URL}/${formData.company_id}`;
        
        // Optionally show a pending notification (assuming onUpdateSuccess handles this)
        if (onUpdateSuccess) onUpdateSuccess({ message: `Updating ${formData.company_name}...`, type: 'info' });

        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    // Add other headers like Authorization if needed
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                console.log('Company successfully updated:', result);
                if (onUpdateSuccess) onUpdateSuccess({ 
                    message: `✅ Company '${result.company_name || formData.company_name}' updated successfully!`, 
                    type: 'success' 
                });
                // The main Companies component should handle refetching the list here if needed
            } else {
                console.error('Update failed:', result);
                if (onUpdateSuccess) onUpdateSuccess({ 
                    message: `❌ Error updating company: ${result.message || response.statusText}.`, 
                    type: 'error' 
                });
            }

        } catch (error) {
            console.error('Network or parsing error during update:', error);
            if (onUpdateSuccess) onUpdateSuccess({ 
                message: "⚠️ A network error occurred during update. Please try again.", 
                type: 'error' 
            });
        }
        
        setShowInfo(null); // Close the modal after submission attempt
    };
    
    // 4. FIELD CONFIGURATION
    // Type definitions: 'span' (contentEditable), 'select', 'date', 'static'
    const fieldsToRender = [
        ['posts', 'Roles/Posts', 'span', false],
        ['job_type', 'Job Type', 'select', false],
        ['ctc_min', 'CTC Min (LPA)', 'span', false],
        ['ctc_max', 'CTC Max (LPA)', 'span', false],
        ['visit_date', 'Visit Date', 'date', false], 
        ['location', 'Location Type', 'select', false],
        ['status', 'Company Status', 'select', false],
        ['applied_students', 'Applied Students', 'static', false], 
        ['selected_students', 'Selected Students', 'static', false], 
    ];

    // 5. RENDER FUNCTION (Unchanged)
    return (
        <div className="company-info-container" ref={wrapperRef}>
            <form className="info-company" onSubmit={handleFinalSubmit}> 
                
                {/* 1. HEADER (Company Name) */}
                <div className='form-field header-field'>
                    <div style={{display: 'flex', alignItems: 'center', gap: '5px'}}>
                        <h2> 
                            <span 
                                id="company_name" 
                                ref={el => fieldRefs.current['company_name'] = el} 
                                contentEditable={editableField === 'company_name'} 
                                onBlur={handleBlur}
                                onKeyDown={handleKeyDown}
                                suppressContentEditableWarning={true}
                            > 
                                {formData.company_name} 
                            </span>
                        </h2>
                        <button 
                            type="button" 
                            className="edit-btn" 
                            onClick={() => handleEditClick('company_name')}
                        > 
                            {editableField === 'company_name' ? '✓' : '✎'}
                        </button>
                    </div>

                    <div>
                        <button type="button" className="close-btn" onClick={() => setShowInfo(null)}> 
                            &times; 
                        </button>
                    </div>
                </div>

                {/* 2. DYNAMIC FIELDS */}
                {fieldsToRender.map(([key, label, type, isLarge]) => {
                    if (key === 'company_name') return null; // Skip header field

                    const isCurrentEditable = editableField === key;
                    const isStatic = type === 'static';

                    return (
                        <div 
                            className='form-field' 
                            key={key} 
                            style={isLarge ? {gridColumn: '1 / -1'} : {}}
                        >
                            <label htmlFor={key}>{label}</label>
                            
                            {/* --- STATIC (Read-only) FIELD with View Button --- */}
                            {isStatic && (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <div className="static-field-value" style={{ flexGrow: 1 }}>
                                        {formData[key]}
                                    </div>
                                    <button 
                                        type="button" 
                                        className="edit-btn" 
                                        onClick={() => handleViewClick(key)}
                                        // Added simple styling for button consistency
                                        style={{ padding: '5px 10px', whiteSpace: 'nowrap' }} 
                                    > 
                                        View 
                                    </button>
                                </div>
                            )}

                            {/* --- SELECT FIELD --- */}
                            {type === 'select' && (
                                <select 
                                    id={key} 
                                    name={key} 
                                    value={formData[key] || ''} 
                                    onChange={handleInputChange} 
                                    ref={el => fieldRefs.current[key] = el}
                                    onFocus={() => setEditableField(key)}
                                >
                                    <option value="">{`Select ${label.split(' ')[0]}`}</option>
                                    {dropdownOptions[key].map(opt => (
                                        <option key={opt} value={opt}>
                                            {opt.replace('_', ' ')}
                                        </option>
                                    ))}
                                </select>
                            )}

                            {/* --- DATE INPUT FIELD --- */}
                            {type === 'date' && (
                                <input 
                                    type="date"
                                    id={key} 
                                    name={key} 
                                    value={formData[key] || ''} 
                                    onChange={handleInputChange} 
                                    ref={el => fieldRefs.current[key] = el}
                                    onFocus={() => setEditableField(key)}
                                />
                            )}
                            
                            {/* --- CONTENT EDITABLE SPAN FIELD (Default) --- */}
                            {type === 'span' && (
                                <div style={{display: 'flex', alignItems: 'center', gap: '5px'}}>
                                    <span 
                                        id={key}
                                        ref={el => fieldRefs.current[key] = el} 
                                        contentEditable={isCurrentEditable} 
                                        onBlur={handleBlur}
                                        onKeyDown={handleKeyDown}
                                        suppressContentEditableWarning={true}
                                        className="editable-content-span" 
                                        style={{
                                            border: isCurrentEditable ? '1px solid #333' : '1px solid transparent',
                                            padding: '0.25em 0.5em',
                                            borderRadius: '4px',
                                            flexGrow: 1,
                                            minHeight: '40px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            backgroundColor: isCurrentEditable ? '#fff' : '#f0f0f0',
                                            boxSizing: 'border-box',
                                        }}
                                    > 
                                        {formData[key]} 
                                    </span>
                                    
                                    <button 
                                        type="button" 
                                        className="edit-btn" 
                                        onClick={() => handleEditClick(key)}
                                    > 
                                        {isCurrentEditable ? '✓' : '✎'}
                                    </button>
                                </div>
                            )}
                        </div>
                    );
                })}
                
                {/* 3. SUBMIT BUTTON */}
                <div className="form-submit-area">
                    <button type="submit" className="submit-form-btn" >Save Changes</button>
                </div>
            </form>
        </div>
    );
};
// End of EditableInfo component

// --- UPDATED Companies COMPONENT ---
// The Companies component needs to pass the notification handler to EditableInfo 
// and handle the list refresh after a successful update.

const Companies = () => {
    const companyListUrl = `${BASE_URL}/api/placements/companies/list`;
    const [companyList, setCompanyList] = useState(null);
    const [addCompany, setAddCompany] = useState(false);
    const [showInfo, setShowInfo] = useState(null);
    const [showFilter, setShowFilter] = useState(false);
    const [filterList, setFilterList] = useState(initialFilterState);
    const searchRef = useRef(null);
    
    // State for asynchronous feedback
    const [notification, setNotification] = useState({ message: '', type: '' });

    // State to hold all form data, initialized to blank values
    const [formData, setFormData] = useState(initialFormData);

    const fetchList = async ()=>{
        const filterContent = objectToQueryString(filterList);
        console.log(filterContent);
        const response = await fetch(companyListUrl + filterContent);
        const data = await response.json();
        
        console.log("Fetched company list:", data);
        setCompanyList(data);
    };

    useEffect(()=>{fetchList()}, []);

    // Generic handler for input/select changes
    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevData => ({
            ...prevData,
            [name]: value
        }));
    };

    const handleFilterChange = (e) => {
        const {name, value} = e.target;
        setFilterList(prev => (
            {
                ...prev,
                [name] : value
            }
        )) 
    }

    useEffect(()=>{
        console.log('use effect [filterlist] : ', filterList);
    }, [filterList])
    
    // Handler for "Add Company" submission (POST)
    const handleFormSubmit = async (e) => {
        e.preventDefault(); 
        
        // 1. Show a pending/loading notification immediately (optional, but good UX)
        setNotification({ message: 'Adding company...', type: 'info' });

        // 2. Clear the form data immediately so the user can see the form reset
        setFormData(initialFormData);
        setAddCompany(false); // Close the modal immediately

        // 3. Perform the asynchronous operation
        try {
            const response = await fetch(COMPANY_CREATE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            // 4. Update UI based on API response
            if (response.ok) {
                console.log('Company successfully added:', result);
                setNotification({ 
                    message: `✅ Company '${result.company_name || formData.company_name}' added successfully!`, 
                    type: 'success' 
                });
                // Refetch the list to update the main view
                fetchList();
            } else {
                console.error('Submission failed:', result);
                setNotification({ 
                    message: `❌ Error adding company: ${result.message || response.statusText}.`, 
                    type: 'error' 
                });
            }

        } catch (error) {
            console.error('Network or parsing error:', error);
            setNotification({ 
                message: "⚠️ A network error occurred. Please try again.", 
                type: 'error' 
            });
        }
    };

    // Handler to manage notifications and optionally trigger a refetch
    const handleUpdateFeedback = (feedback) => {
        setNotification({ message: feedback.message, type: feedback.type });
        // Refetch the list only on successful update
        if (feedback.type === 'success') {
            fetchList();
        }
    };

    // Handler to manually close the notification
    const closeNotification = () => {
        setNotification({ message: '', type: '' });
    }

    // UPDATED RENDER: Pass handleUpdateFeedback to EditableInfo
    return (
        <div className="company-container">
            
            <Notification 
                message={notification.message} 
                type={notification.type} 
                onClose={closeNotification} 
            />
            
            <div className="search-bar">
                <div className="search-input-group">
                    <input name="query" type="text" placeholder="search company name, post or id" onChange={handleFilterChange}></input>
                    <div className="clickables">
                        <button className="filter-button" onClick={()=>setShowFilter(!showFilter)}>Filter</button> 
                        <button className="search-button" onClick={fetchList}>Search</button>
                        { showFilter && (<CompanyFilter  oldFilter={filterList} onApplyFilter={(e)=>{
                            const old_query = filterList?.query || '';
                            console.log("present list", e);
                            setFilterList(e);
                            setFilterList(prev => (
                                {
                                    ...prev,
                                    query : old_query
                                }
                            ))
                        }} showSet={setShowFilter}/>) }
                    </div>
                </div>
                <button className="add-company-button" onClick={()=>setAddCompany(true)}>Add Company +</button>
            </div>
            
            {
                addCompany && (
                <div className="add-company-container">
                    <form className='add-company' onSubmit={handleFormSubmit}>
                        
                        {/* Header and Close Button */}
                        <div className='form-field header-field'>
                            <h2>Add Company</h2>
                            <button type="button" className="close-btn" onClick={()=>setAddCompany(false)}> &times; </button>
                        </div>
                        
                        {/* Company Name */}
                        <div className='form-field'>
                            <label htmlFor='company_name'>Company Name *</label>
                            <input id="company_name" name="company_name" 
                                   placeholder='e.g., Google, Tesla' required 
                                   value={formData.company_name} onChange={handleFormChange} />
                        </div>

                        {/* Posts/Roles */}
                        <div className='form-field'>
                            <label htmlFor='posts'>Roles/Posts *</label>
                            <input id="posts" name="posts" 
                                   placeholder="e.g., SDE, SWE, Analyst" required 
                                   value={formData.posts} onChange={handleFormChange} />
                        </div>

                        {/* Job Type Dropdown */}
                        <div className='form-field'>
                            <label htmlFor='job_type'>Job Type *</label>
                            <select id="job_type" name="job_type" required 
                                    value={formData.job_type} onChange={handleFormChange}>
                                <option value={''}>Select Job Type</option>
                                <option value={'Full_Time'}>Full Time</option>
                                <option value={'Internship'}>Internship</option>
                                <option value={'Both'}>Both</option>
                            </select>
                        </div>

                        {/* CTC Min */}
                        <div className='form-field'>
                            <label htmlFor='ctc_min'>CTC Min (LPA)</label>
                            <input id="ctc_min" name="ctc_min" type="number" placeholder="10" 
                                   value={formData.ctc_min} onChange={handleFormChange} />
                        </div>

                        {/* CTC Max */}
                        <div className='form-field'>
                            <label htmlFor='ctc_max'>CTC Max (LPA)</label>
                            <input id="ctc_max" name="ctc_max" type="number" placeholder="25" 
                                   value={formData.ctc_max} onChange={handleFormChange} />
                        </div>

                        {/* Visit Date */}
                        <div className='form-field'>
                            <label htmlFor='visit_date'>Visit Date</label>
                            <input id="visit_date" name="visit_date" type="date" 
                                   value={formData.visit_date} onChange={handleFormChange} />
                        </div>

                        {/* Location Dropdown */}
                        <div className='form-field'>
                            <label htmlFor='location'>Location Type *</label>
                            <select id="location" name="location" required 
                                    value={formData.location} onChange={handleFormChange}>
                                <option value={''}>Select Location</option>
                                <option value={'Onsite'}>On-Site</option>
                                <option value={'Remote'}>Remote</option>
                                <option value={'Hybrid'}>Hybrid</option>
                            </select>
                        </div>

                        {/* Status Dropdown */}
                        <div className='form-field'>
                            <label htmlFor='status'>Company Status *</label>
                            <select id="status" name="status" required 
                                    value={formData.status} onChange={handleFormChange}>
                                <option value={''}>Select Status</option>
                                <option value={'Upcoming'}>Upcoming</option>
                                <option value={'Visited'}>Visited</option>
                                <option value={'Rejected'}>Rejected</option>
                                <option value={'Pending'}>Pending</option>
                            </select>
                        </div>

                        {/* Submit Button (Spans both columns via form-submit-area CSS) */}
                        <div className="form-submit-area">
                            <button type="submit" className="submit-form-btn">Add Company</button>
                        </div>
                    </form>
                </div>
            )}

            {
                showInfo && 
                <EditableInfo 
                    data={showInfo} 
                    setShowInfo={setShowInfo} 
                    onUpdateSuccess={handleUpdateFeedback} // Pass handler to update notification and list
                />
            }        

            <div className="company-list">
                {
                    companyList && companyList.data.map((comp, indx)=>(<Company key={indx} data={comp} setShowInfo={setShowInfo}/>))
                }
            </div>
        </div>
    );
};

export default Companies;