package com.hubert.blog.service;

import com.hubert.blog.dto.AuthResponse;
import com.hubert.blog.dto.RegisterRequest;
import com.hubert.blog.model.User;
import com.hubert.blog.repository.UserRepository;
import com.hubert.blog.security.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {

    private final AuthenticationManager authenticationManager;
    private final JwtService jwtService;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public User register(RegisterRequest request){
        if(userRepository.findByUserName(request.getUserName()).isPresent()){
            throw new RuntimeException("User with this name already exists!");
        }

        User user = new User();
        user.setUserName(request.getUserName());
        user.setPassword(passwordEncoder.encode(request.getPassword()));

        return userRepository.save(user);
    }

    public AuthResponse login(RegisterRequest request) { // lub LoginRequest
        // 1. To automatycznie sprawdzi hasło. Jak będzie złe, rzuci wyjątek.
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getUserName(),
                        request.getPassword()
                )
        );

        // 2. Jeśli przeszło, szukamy usera i generujemy token
        var user = userRepository.findByUserName(request.getUserName())
                .orElseThrow();
        var jwtToken = jwtService.generateToken(user);

        return new AuthResponse(jwtToken);
    }
}
