import React from "react";

import PageNotFound from "./components/PageNotFound/PageNotFound";
import Home from "./components/Home/Home";

export const router = [
  {
    path: "*",
    element: <PageNotFound />,
  },
  {
    path: "/",
    element: <Home />,
  },
];