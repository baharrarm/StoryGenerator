import React, { useContext } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Box, Container, Group, Button, Text } from "@mantine/core";
import { AuthContext } from "../AuthContext";

export default function Layout({ children }) {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const isActive = (p) => pathname === p || pathname.startsWith(p + "/");

  const logout = () => {
    localStorage.removeItem("cog_at");
    setUser(null);
    navigate("/login");
  };

  return (
    <>
      <Container size="lg" px="md" pt="md" pb={72 /* space for bottom bar */}>
        {children}
      </Container>

      <Box
        component="nav"
        pos="fixed"
        bottom={0}
        left={0}
        right={0}
        bg="var(--mantine-color-body)"
        style={{ borderTop: "1px solid var(--mantine-color-default-border)", zIndex: 100 }}
        px="md"
        py="xs"
      >
        <Container size="lg">
          <Group justify="space-between">
            <Group gap="md">
              <Text
                fw={700}
                component={Link}
                to="/"
                style={{ textDecoration: "none", color: "inherit" }}
              >
                GenStory
              </Text>

              <Button
                variant={isActive("/") ? "filled" : "subtle"}
                component={Link}
                to="/"
              >
                Generate
              </Button>

              {user && (
                <>
                  <Button
                    variant={isActive("/mystories") ? "filled" : "subtle"}
                    component={Link}
                    to="/mystories"
                  >
                    My Stories
                  </Button>
                  <Button
                    variant={isActive("/profile") ? "filled" : "subtle"}
                    component={Link}
                    to="/profile"
                  >
                    Profile
                  </Button>
                </>
              )}

              {/* {user?.role === "admin" && ( */}
              {(user?.role === "admin" || user?.groups?.includes("Admin")) && (
                <Button
                  variant={isActive("/admin") ? "filled" : "subtle"}
                  component={Link}
                  to="/admin"
                >
                  Admin
                </Button>
              )}
            </Group>

            {!user ? (
              <Group>
                <Button
                  variant={isActive("/login") ? "filled" : "light"}
                  component={Link}
                  to="/login"
                >
                  Login
                </Button>
                <Button
                  variant={isActive("/register") ? "filled" : "subtle"}
                  component={Link}
                  to="/register"
                >
                  Register
                </Button>
              </Group>
            ) : (
              <Button color="red" variant="light" onClick={logout}>
                Logout
              </Button>
            )}
          </Group>
        </Container>
      </Box>
    </>
  );
}
