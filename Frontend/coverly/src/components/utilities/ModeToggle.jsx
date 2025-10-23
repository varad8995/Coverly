import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Moon, Sun } from "lucide-react";
import { toggleDarkMode } from "../../redux/homeSlice";
import { useNavigate } from "react-router-dom";
import { Menu, MenuItem } from "@mui/material";
import Box from "@mui/material/Box";
import ListItemIcon from "@mui/material/ListItemIcon";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import { supabase } from "../../api/supabaseClient.js";
import { clearUser } from "../../redux/authSlice.js";

export default function ModeToggle() {
  let navigate = useNavigate();
  const dispatch = useDispatch();
  const { isDarkMode, user } = useSelector((state) => ({
    isDarkMode: state.home.isDarkMode,
    user: state.auth.user,
  }));
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const menuBg = isDarkMode ? "bg-zinc-900 border-zinc-700" : "bg-white border-gray-200";
  const iconColor = isDarkMode ? "#e5e5e5" : "#333333";

  useEffect(() => {
    console.log(user);
  }, []);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    setAnchorEl(null);
    await supabase.auth.signOut();
    dispatch(clearUser());
    navigate("/");
  };

  return (
    <>
      <Box sx={{ display: "flex", alignItems: "center", textAlign: "center" }}>
        <Tooltip title="Account settings">
          <IconButton
            onClick={handleClick}
            size="small"
            sx={{
              ml: 2,
              color: iconColor,
              transition: "background-color 0.3s ease",
              "&:hover": {
                backgroundColor: isDarkMode ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.05)",
              },
            }}
            aria-controls={open ? "account-menu" : undefined}
            aria-haspopup="true"
            aria-expanded={open ? "true" : undefined}
          >
            <img
              src={user.user_metadata.avatar_url}
              alt="Profile"
              className="w-12 h-12 rounded-full border border-gray-300 dark:border-zinc-700 shadow-sm object-cover ml-auto"
            />
          </IconButton>
        </Tooltip>
      </Box>
      <Menu
        anchorEl={anchorEl}
        id="account-menu"
        open={open}
        onClose={handleClose}
        onClick={handleClose}
        slotProps={{
          paper: {
            elevation: 0,
            className: `
        ${menuBg}
        border
        rounded-2xl
        shadow-xl
        py-2
        w-64
        transition-colors
        duration-300
      `,
            sx: {
              overflow: "visible",
              filter: "drop-shadow(0px 4px 16px rgba(0,0,0,0.25))",
              mt: 1.5,
              "&::before": {
                content: '""',
                display: "block",
                position: "absolute",
                top: 0,
                right: 18,
                width: 12,
                height: 12,
                bgcolor: isDarkMode ? "#18181b" : "#fff",
                transform: "translateY(-50%) rotate(45deg)",
                zIndex: 0,
                borderTop: isDarkMode ? "1px solid #27272a" : "1px solid #e5e7eb",
                borderLeft: isDarkMode ? "1px solid #27272a" : "1px solid #e5e7eb",
              },
            },
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        {/* USER INFO */}
        <MenuItem
          disableRipple
          className="flex items-center justify-between gap-4 px-4 py-3 border-b border-gray-200 dark:border-zinc-700"
        >
          <div className="flex flex-col text-left">
            <span className={`text-md font-semibold text-gray-900`}>{user.user_metadata.full_name}</span>
            <span className={`text-xs font-medium text-gray-900 truncate`}>{user.user_metadata.email}</span>
          </div>
          {/* <img
            src={user.user_metadata.avatar_url}
            alt="Profile"
            className="w-12 h-12 rounded-full border border-gray-300 dark:border-zinc-700 shadow-sm object-cover ml-auto"
          /> */}
        </MenuItem>

        {/* THEME TOGGLE */}
        <MenuItem
          className="flex items-center justify-between w-full gap-4 px-4 py-2 hover:bg-gray-100 dark:hover:bg-zinc-800 transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          <span className={`text-sm font-medium text-gray-900`}>Change theme</span>
          <div className="flex justify-end w-auto ml-auto">
            <button
              onClick={() => dispatch(toggleDarkMode())}
              className={`relative w-14 h-7 rounded-full ${
                isDarkMode ? "bg-zinc-800 border border-zinc-700" : "bg-gradient-to-r from-purple-400 to-pink-400"
              } transition-colors duration-300 shadow-inner`}
            >
              <div
                className={`absolute top-0.5 ${isDarkMode ? "right-0.5" : "left-0.5"} w-6 h-6 rounded-full ${
                  isDarkMode ? "bg-gradient-to-br from-zinc-700 to-zinc-900" : "bg-white"
                } shadow-md transition-all duration-300 flex items-center justify-center`}
              >
                {isDarkMode ? <Moon className="w-3 h-3 text-zinc-300" /> : <Sun className="w-3 h-3 text-orange-500" />}
              </div>
            </button>
          </div>
        </MenuItem>

        {/* LOGOUT */}
        <MenuItem
          onClick={handleLogout}
          className="flex items-center justify-between w-full gap-4 px-4 py-2 hover:bg-red-50 dark:hover:bg-zinc-800 transition-colors"
        >
          <span className={`text-sm font-medium text-gray-900`}>Logout</span>
          <ListItemIcon className="min-w-0 ml-auto flex justify-end ml-auto">
            <LogoutRoundedIcon
              fontSize="small"
              sx={{
                color: isDarkMode ? "#f87171" : "#dc2626",
                transition: "color 0.3s ease",
              }}
            />
          </ListItemIcon>
        </MenuItem>
      </Menu>
    </>
  );
}
