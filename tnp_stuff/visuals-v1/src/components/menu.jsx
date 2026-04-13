// DropdownMenu.js
import React, { useState, useEffect, useRef } from "react";
import "./dropdown.css";

// Classes for menu structure
class MenuItem {
  constructor(name, list = null, onClick = null) {
    this.name = name;
    this.list = list;
    this.onClick = onClick ? onClick : () => console.log("Clicked:", this.name);
  }
}

class DropdownList {
  constructor(...options) {
    this.list = options;
  }

  render(resetTrigger = 0) {
    return <DropdownListComponent list={this.list} resetTrigger={resetTrigger} />;
  }
}

// Component for list with accordion behavior
const DropdownListComponent = ({ list, resetTrigger }) => {
  const [openIndex, setOpenIndex] = useState(null);

  // Reset openIndex when resetTrigger changes
  useEffect(() => {
    setOpenIndex(null);
  }, [resetTrigger]);

  const handleToggle = (idx) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <ul className="dropdown-list">
      {list.map((item, idx) => (
        <DropdownItem
          key={idx}
          item={item}
          isOpen={openIndex === idx}
          toggle={() => handleToggle(idx)}
          resetTrigger={resetTrigger}
        />
      ))}
    </ul>
  );
};

// Dropdown item component
const DropdownItem = ({ item, isOpen, toggle, resetTrigger }) => {
  const hasSubmenu = item.list !== null;

  const handleClick = (e) => {
    e.stopPropagation(); // prevent bubbling to document
    if (hasSubmenu) {
      toggle(); // toggle submenu
    } else {
      item.onClick();
    }
  };

  return (
    <li className={`dropdown-item ${hasSubmenu ? "has-submenu" : ""}`}>
      <div className="dropdown-title" onClick={handleClick}>
        {item.name} {hasSubmenu && <span className="indicator">{isOpen ? "-" : "+"}</span>}
      </div>
      {hasSubmenu && isOpen && (
        <div className="submenu">{item.list.render(resetTrigger)}</div>
      )}
    </li>
  );
};

// Main Dropdown Menu component
export default function DropdownMenu() {
  const menuRef = useRef(null);
  const [resetTrigger, setResetTrigger] = useState(0);

  // Click outside to close all menus
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setResetTrigger((prev) => prev + 1); // increment trigger to reset all
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  // Example menu structure
  const menuItems = new DropdownList(
    new MenuItem(
      "Home",
      new DropdownList(
        new MenuItem(
          "Item 1",
          new DropdownList(
            new MenuItem(
              "Sub Item 1.1",
              new DropdownList(
                new MenuItem("Sub Sub Item 1.1.1"),
                new MenuItem("Sub Sub Item 1.1.2")
              )
            ),
            new MenuItem("Sub Item 1.2"),
            new MenuItem("Sub Item 1.3", new DropdownList(new MenuItem("Sub Sub Item 1.3.1")))
          )
        ),
        new MenuItem("Item #2"),
        new MenuItem("Item 3")
      )
    ),
    new MenuItem(
      "Tables",
      new DropdownList(
        new MenuItem("Table 1"),
        new MenuItem("Table 2"),
        new MenuItem(
          "More Tables",
          new DropdownList(
            new MenuItem("Table 3"),
            new MenuItem("Table 4", new DropdownList(new MenuItem("Table 4a")))
          )
        )
      )
    ),
    new MenuItem("About"),
    new MenuItem(
      "Services",
      new DropdownList(
        new MenuItem("Web Development"),
        new MenuItem("App Development"),
        new MenuItem(
          "Marketing",
          new DropdownList(
            new MenuItem("SEO"),
            new MenuItem("Content Marketing"),
            new MenuItem("Social Media")
          )
        )
      )
    ),
    new MenuItem("Contact")
  );

  return (
    <nav className="navbar" ref={menuRef}>
      {menuItems.render(resetTrigger)}
    </nav>
  );
}
