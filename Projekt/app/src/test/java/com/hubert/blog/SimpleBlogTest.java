package com.hubert.blog;

import com.hubert.blog.dto.RegisterRequest;
import com.hubert.blog.model.User;
import com.hubert.blog.repository.UserRepository;
import com.hubert.blog.security.JwtService;
import com.hubert.blog.service.UserService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;

@ExtendWith(MockitoExtension.class)
public class SimpleBlogTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private AuthenticationManager authenticationManager;

    @Mock
    private JwtService jwtService;

    @InjectMocks
    private UserService userService; // Mockito automatycznie wstrzyknie powyższe atrapy do Twojego serwisu

    @Test
    public void register_ShouldSaveUser_WhenUserDoesNotExist() {
        // 1. Przygotowanie danych (Given)
        RegisterRequest request = new RegisterRequest();
        request.setUserName("hubert_test");
        request.setPassword("plainPassword");

        // Definiujemy zachowanie atrap (stubbing)
        Mockito.when(userRepository.findByUserName("hubert_test")).thenReturn(Optional.empty());
        Mockito.when(passwordEncoder.encode("plainPassword")).thenReturn("encodedPassword");

        // Mockujemy zachowanie metody save, by zwracała poprawnie zapisany obiekt z nadanym ID
        Mockito.when(userRepository.save(any(User.class))).thenAnswer(invocation -> {
            User userToSave = invocation.getArgument(0);
            userToSave.setId(1L); // Symulujemy automatyczne nadanie ID przez bazę danych
            return userToSave;
        });

        // 2. Wykonanie testowanej metody (When)
        User savedUser = userService.register(request);

        // 3. Sprawdzenie poprawności (Then)
        assertNotNull(savedUser);
        assertEquals(1L, savedUser.getId());
        assertEquals("hubert_test", savedUser.getUserName());
        assertEquals("encodedPassword", savedUser.getPassword());

        // Weryfikacja czy metody na atrapach zostały wywołane dokładnie 1 raz
        Mockito.verify(userRepository, Mockito.times(1)).findByUserName("hubert_test");
        Mockito.verify(passwordEncoder, Mockito.times(1)).encode("plainPassword");
        Mockito.verify(userRepository, Mockito.times(1)).save(any(User.class));
    }

    @Test
    public void register_ShouldThrowException_WhenUserAlreadyExists() {
        // 1. Przygotowanie danych (Given)
        RegisterRequest request = new RegisterRequest();
        request.setUserName("existing_user");
        request.setPassword("password");

        User existingUser = new User();
        existingUser.setUserName("existing_user");

        // Definiujemy zachowanie atrapy - baza twierdzi, że taki użytkownik już istnieje
        Mockito.when(userRepository.findByUserName("existing_user")).thenReturn(Optional.of(existingUser));

        // 2. Wykonanie i asercja wyjątku (When & Then)
        RuntimeException exception = assertThrows(RuntimeException.class, () -> {
            userService.register(request);
        });

        assertEquals("User with this name already exists!", exception.getMessage());

        // Weryfikacja: metoda save nie powinna być nigdy wywołana, ponieważ rzucono wyjątek wcześniej
        Mockito.verify(userRepository, Mockito.never()).save(any(User.class));
    }
}