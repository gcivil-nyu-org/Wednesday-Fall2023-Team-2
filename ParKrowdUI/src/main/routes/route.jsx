/** @format */

import React, { lazy } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

const App = lazy(() => import("../../App"));

const routeConfig = function () {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<App />} />

        {/* if no matching URL, default redirect to home page */}
        <Route path='*' element={<Navigate to='/' />} />
      </Routes>
    </Router>
  );
};

export default routeConfig;
