/****************************************************
 * Sección 1: Funciones para llamadas a la API
 ****************************************************/

/**
 * Realiza una solicitud para obtener los usuarios paginados.
 * @param {number} page - La página que se desea cargar.
 * @param {number} usersPerPage - Número de usuarios por página.
 * @returns {Promise<object>} Objeto con la lista de usuarios y el total de páginas.
 */
async function fetchUsers(page = 1, usersPerPage = 5) {
  try {
    const response = await fetch(
      `http://localhost:8000/users_paginated?page=${page}&per_page=${usersPerPage}`
    );
    if (!response.ok) throw new Error("Error al obtener los datos.");
    const data = await response.json();
    return { users: data.users, totalPages: data.total_pages };
  } catch (error) {
    console.error("Error al obtener los datos:", error);
    document.querySelector("#users-table tbody").innerHTML = `
        <tr><td colspan="5" style="text-align:center; color:red;">Error cargando usuarios</td></tr>`;
    return { users: [], totalPages: 1 };
  }
}

/****************************************************
 * Sección 2: Funciones para el manejo de modales
 ****************************************************/

/**
 * Inicializa y configura el modal de creación de usuario.
 */
function handleUserModal() {
  const createBtn = document.getElementById("create-btn");
  const userModalElement = document.getElementById("userModal");
  const userModal = new bootstrap.Modal(userModalElement);

  createBtn.addEventListener("click", () => {
    // Aquí podrías cargar dinámicamente opciones de permisos y áreas,
    // si se requiere, mediante una función como loadPermissionsAndAreasForCreate().
    userModal.show();
  });

  const userForm = document.getElementById("user-form");

  userForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userData = {
      str_name_user: document.getElementById("username").value,
      str_email: document.getElementById("email").value,
      str_password: document.getElementById("password").value,
    };

    try {
      const response = await fetch("http://localhost:8000/users/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Usuario Registrado:", data.message);
        userModal.hide();
        userForm.reset();
        Swal.fire({
          title: "¡Éxito!",
          text: "Usuario registrado correctamente.",
          icon: "success",
          timer: 2000,
          showConfirmButton: false,
        }).then(() => {
          location.reload();
        });
      } else {
        const errorData = await response.json();
        console.error("Error al registrar el usuario:", errorData.detail);
        alert("Error al registrar el usuario: " + errorData.detail);
      }
    } catch (error) {
      console.error("Error de red:", error);
      alert("Hubo un problema al intentar registrar el usuario.");
    }
  });
}

/**
 * Función dummy para cargar permisos y áreas en el modal de creación.
 * Implementa la lógica según tus necesidades.
 */
function loadPermissionsAndAreasForCreate() {
  console.log("Cargando permisos y áreas para crear usuario...");
}

/**
 * Función dummy para cargar permisos y áreas en el modal de edición.
 * @param {number} selectedPermission - Permiso seleccionado.
 * @param {number} selectedArea - Área seleccionada.
 */
function loadPermissionsAndAreas(selectedPermission, selectedArea) {
  console.log(
    "Cargando permisos y áreas para edición...",
    selectedPermission,
    selectedArea
  );
}

/****************************************************
 * Sección 3: Funcionalidad principal (Usuarios)
 ****************************************************/

let currentPage = 1;
let totalPages = 1;
const usersPerPage = 5;

document.addEventListener("DOMContentLoaded", () => {
  // Inicializa el manejo de modales
  handleUserModal();

  // Asignar listeners para búsqueda y paginación
  document
    .getElementById("search-input")
    .addEventListener("input", searchUsers);
  document
    .getElementById("prev-page")
    .addEventListener("click", () => changePage(-1));
  document
    .getElementById("next-page")
    .addEventListener("click", () => changePage(1));

  // Manejar botón de cierre de sesión
  document.getElementById("logout-btn").onclick = async function () {
    const response = await fetch("/logout", { method: "POST" });
    if (response.ok) {
      window.location.href = "/";
    }
  };

  // Renderiza la primera página de usuarios
  renderUsers(currentPage);
});

/**
 * Renderiza la tabla de usuarios para la página indicada.
 * @param {number} page - La página a renderizar.
 */
async function renderUsers(page) {
  const { users, totalPages: tp } = await fetchUsers(page, usersPerPage);
  totalPages = tp;
  const tbody = document.querySelector("#users-table tbody");
  tbody.innerHTML = "";

  users.forEach((user) => {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${user.username}</td>
        <td>${user.email}</td>
        <td>${user.password}</td>
        <td class="action-cell">
          <button class="action-btn edit-btn" onclick="editUser(${user.id})"><i class="fas fa-edit"></i></button>
          <button class="action-btn delete-btn" onclick="deleteUser(${user.id})"><i class="fas fa-trash-alt"></i></button>
        </td>
      `;
    tbody.appendChild(row);
  });

  document.getElementById(
    "page-info"
  ).textContent = `Página ${currentPage} de ${totalPages}`;
  document.getElementById("prev-page").disabled = currentPage === 1;
  document.getElementById("next-page").disabled = currentPage === totalPages;
}

/**
 * Cambia la página actual y renderiza los nuevos usuarios.
 * @param {number} direction - Dirección del cambio (-1 o 1).
 */
function changePage(direction) {
  if (
    (direction === -1 && currentPage > 1) ||
    (direction === 1 && currentPage < totalPages)
  ) {
    currentPage += direction;
    document.getElementById("search-input").value = "";
    renderUsers(currentPage);
  }
}

/**
 * Realiza la búsqueda de usuarios según el input.
 */
async function searchUsers() {
  const query = document.getElementById("search-input").value.toLowerCase();
  if (query.trim() === "") return renderUsers(currentPage);

  try {
    const response = await fetch(
      `http://localhost:8000/users_search?query=${encodeURIComponent(query)}`
    );
    if (!response.ok) throw new Error("Error al buscar usuarios.");
    const data = await response.json();
    const tbody = document.querySelector("#users-table tbody");
    tbody.innerHTML = "";

    data.users.forEach((user) => {
      const row = document.createElement("tr");
      row.innerHTML = `
          <td>${user.username}</td>
          <td>${user.email}</td>
          <td>${user.password}</td>
          <td class="action-cell">
            <button class="action-btn edit-btn" onclick="editUser(${user.id})"><i class="fas fa-edit"></i></button>
            <button class="action-btn delete-btn" onclick="deleteUser(${user.id})"><i class="fas fa-trash-alt"></i></button>
          </td>
        `;
      tbody.appendChild(row);
    });

    document.getElementById("page-info").textContent = `Resultados de búsqueda`;
    document.getElementById("prev-page").disabled = true;
    document.getElementById("next-page").disabled = true;
  } catch (error) {
    console.error("Error al buscar usuarios:", error);
  }
}

/**
 * Función para editar el usuario.
 * @param {number} userId - ID del usuario a editar.
 */
function editUser(userId) {
  console.log("Editando usuario con ID:", userId);
  fetch(`http://localhost:8000/userById/${userId}`)
    .then((response) => {
      if (!response.ok) throw new Error("Error en la respuesta del servidor");
      return response.json();
    })
    .then((user) => {
      document.getElementById("edit-user-id").value = userId;
      document.getElementById("edit-username").value = user.username || "";
      document.getElementById("edit-password").value = user.password || "";
      document.getElementById("edit-email").value = user.email || "";

      loadPermissionsAndAreas(user.id_permission, user.id_area);

      const editUserModal = new bootstrap.Modal(
        document.getElementById("editUserModal")
      );
      editUserModal.show();

      const editUserForm = document.getElementById("edit-user-form");
      editUserForm.onsubmit = (event) => {
        event.preventDefault();
        const formData = new FormData(editUserForm);
        fetch(`http://localhost:8000/usersUpdate/${userId}`, {
          method: "PUT",
          body: formData,
        })
          .then((response) => {
            if (!response.ok) throw new Error("Error al actualizar el usuario");
            return response.json();
          })
          .then((data) => {
            Swal.fire({
              title: "¡Éxito!",
              text: data.message || "Usuario actualizado exitosamente",
              icon: "success",
              timer: 2000,
              showConfirmButton: false,
            }).then(() => {
              editUserModal.hide();
              location.reload();
            });
          })
          .catch((error) => {
            console.error("Error al actualizar usuario:", error);
            Swal.fire({
              title: "¡Error!",
              text: "Error al actualizar usuario.",
              icon: "error",
              timer: 2000,
              showConfirmButton: false,
            });
          });
      };
    })
    .catch((error) => {
      console.error("Error al obtener usuario:", error);
    });
}

/**
 * Función para eliminar el usuario.
 * @param {number} userId - ID del usuario a eliminar.
 */
function deleteUser(userId) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        title: "Eliminando...",
        text: "Por favor, espera.",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });
      fetch(`/users/${userId}`, { method: "DELETE" })
        .then((response) => {
          if (response.ok) {
            Swal.fire({
              title: "¡Eliminado!",
              text: "El usuario ha sido eliminado correctamente.",
              icon: "success",
              timer: 2000,
              showConfirmButton: false,
            });
            renderUsers(currentPage);
          } else {
            Swal.fire({
              title: "Error",
              text: "Hubo un problema al eliminar el usuario.",
              icon: "error",
            });
          }
        })
        .catch((error) => {
          console.error("Error al eliminar el usuario:", error);
          Swal.fire({
            title: "Error de conexión",
            text: "No se pudo conectar con el servidor.",
            icon: "error",
          });
        });
    }
  });
}
