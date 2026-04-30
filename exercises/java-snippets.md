```java
public Book findBookByTitle(String title) throws SQLException {
    String query = "SELECT * FROM books WHERE title = ?";
    try (PreparedStatement stmt = connection.prepareStatement(query)) {
        stmt.setString(1, title);
        ResultSet rs = stmt.executeQuery();
        if (rs.next()) {
            return new Book(rs.getInt("id"), rs.getString("title"), rs.getBoolean("is_borrowed"));
        }
    }
    return null;
}
```

```java
public boolean borrowBook(String bookTitle, String memberId) {
    Book book = findBookByTitle(bookTitle);
    if (book != null && !book.isBorrowed()) {
        Member member = findMemberById(memberId);
        if (member != null) {
            book.setBorrowed(true);
            return true;
        }
    }
    return false;
}
```

```java

@PostMapping("/book/borrow")
public String borrowBook(@RequestParam String title, @RequestParam int memberId, Model model) {
    boolean success = libraryService.borrowBook(title, memberId);
    if (!success) {
        model.addAttribute("errorMessage", "Failed to borrow the book. Please check the title and member ID.");
        return home(model);
    }
    return "redirect:/library";
}
```

```java
private static void registerMember() {
    System.out.print("Enter member name: ");
    String name = scanner.nextLine();
    Member member = new Member(name);
    library.registerMember(member);
    System.out.println("Member registered.");
}
```

```java
public interface CourseRepository extends JpaRepository<Course, Long> {
}
```

```java
public boolean enrollStudentInCourse(Long studentId, Long courseId) {
    Optional<Student> student = studentRepository.findById(studentId);
    Optional<Course> course = courseRepository.findById(courseId);

    if (student.isPresent() && course.isPresent()) {
        Enrollment enrollment = new Enrollment();
        enrollment.setStudent(student.get());
        enrollment.setCourse(course.get());
        enrollmentRepository.save(enrollment);
        return true;
    }
    return false;
}
```

```java

@KafkaListener(topics = "enroll-student-topic", groupId = "university-group")
public void handleEnrollStudent(EnrollmentRequest enrollmentRequest) {
    Enrollment enrollment = new Enrollment();
    enrollment.setStudentId(enrollmentRequest.getStudentId());
    enrollment.setCourseId(enrollmentRequest.getCourseId());

    enrollmentService.saveEnrollment(enrollment);

    System.out.println("Processed enrollment for student ID " + enrollmentRequest.getStudentId() +
            " in course ID " + enrollmentRequest.getCourseId());
}
```

```java

@PayloadRoot(namespace = NAMESPACE_URI, localPart = "EnrollStudentRequest")
@ResponsePayload
public EnrollStudentResponse enrollStudent(@RequestPayload EnrollStudentRequest request) {
    enrollmentService.enrollStudent(request.getStudentId(), request.getCourseId());

    EnrollStudentResponse response = new EnrollStudentResponse();
    response.setStatus("Success");
    return response;
}
```

```java

@PostMapping
public ResponseEntity<Payment> createPayment(@RequestBody PaymentRequest paymentRequest) {
    try {
        Payment payment = paymentService.processPayment(paymentRequest);
        return new ResponseEntity<>(payment, HttpStatus.CREATED);
    } catch (IllegalArgumentException e) {
        return new ResponseEntity<>(null, HttpStatus.BAD_REQUEST);
    }
}
```

```java
public Payment processPayment(Payment payment) {
    if (isDuplicateTransaction(payment)) {
        throw new IllegalArgumentException("Duplicate transaction detected.");
    }

    double transactionFee = calculateTransactionFee(payment.getAmount());

    Payment updatedPayment = new Payment(
            payment.getAmount(),
            payment.getCurrency(),
            payment.getPaymentMethod(),
            "Processed",
            transactionFee
    );
    updatedPayment.setId(payment.getId());

    return paymentRepository.save(updatedPayment);
}
```

```java
public Payment createPayment(Payment payment) {
    ResponseEntity<Payment> response =
            restTemplate.postForEntity(paymentServiceUrl + "/payments", payment, Payment.class);
    return response.getBody();
}
```

```java
public void sendPayment(Payment payment) {
    PaymentDTO paymentDTO = new PaymentDTO(
            payment.getId(),
            payment.getAmount(),
            payment.getCurrency(),
            payment.getPaymentMethod(),
            payment.getStatus(),
            payment.getTransactionFee()
    );

    kafkaTemplate.send(PAYMENT_TOPIC, paymentDTO);
}
```

```java
public Bet placeBet(Long playerId, double amount, String game) {
    Player player = playerRepository.findById(playerId);
    if (player == null) {
        throw new IllegalArgumentException("Player not found.");
    }

    if (amount > MAX_BET_LIMIT) {
        throw new IllegalArgumentException("Bet amount exceeds the maximum limit.");
    }

    double newBalance = player.getBalance() - amount;
    if (newBalance < MIN_BALANCE_REQUIRED) {
        throw new IllegalArgumentException("Insufficient balance to maintain minimum required.");
    }

    double totalDailyBets = betRepository.findTotalAmountByPlayerAndDate(playerId, java.time.LocalDate.now().toString());
    if (totalDailyBets + amount > DAILY_BET_LIMIT) {
        throw new IllegalArgumentException("Daily bet limit exceeded.");
    }

    boolean result = Math.random() > 0.5;

    player.setBalance(newBalance);
    playerRepository.save(player);

    Bet bet = new Bet(null, player, amount, game, result);
    betRepository.save(bet);

    return bet;
}
```

```java
public Payout processPayout(Long betId) {
    Bet bet = betRepository.findById(betId);
    if (bet == null) {
        throw new IllegalArgumentException("Bet not found.");
    }

    if (!bet.isResult()) {
        throw new IllegalArgumentException("Bet did not win.");
    }

    Player player = bet.getPlayer();
    double payoutAmount = bet.getAmount() * 2;

    double totalBetAmount = betRepository.findTotalAmountByPlayerAndDate(player.getId(), java.time.LocalDate.now().toString());
    double bonus = totalBetAmount * 0.05;
    payoutAmount += bonus;

    player.setBalance(player.getBalance() + payoutAmount);
    playerRepository.save(player);

    Payout payout = new Payout(null, player, payoutAmount);
    payoutRepository.save(payout);

    return payout;
}
```

```java

@Repository
public interface BetRepository extends MongoRepository<Bet, String> {
    List<Bet> findByPlayerId(String playerId);

    double findTotalAmountByPlayerIdAndDate(String playerId, String date);
}
```

```java
public void save(Bet bet) {
    Document doc = new Document("playerId", bet.getPlayerId())
            .append("amount", bet.getAmount())
            .append("game", bet.getGame())
            .append("result", bet.isResult());
    if (bet.getId() != null) {
        doc.append("_id", bet.getId());
    }
    collection.replaceOne(new Document("_id", bet.getId()), doc, new ReplaceOptions().upsert(true));
}
```

```java
public void borrow() {
    if (isBorrowed) {
        throw new IllegalStateException("Book is already borrowed.");
    }
    if (borrowCount >= MAX_BORROW_COUNT) {
        throw new IllegalStateException("This book cannot be borrowed anymore; maximum borrow limit reached.");
    }
    isBorrowed = true;
    borrowCount++;
}
```

```java
public void returnBook() {
    if (borrowedBooksCount == 0) {
        throw new IllegalStateException("No books to return.");
    }
    borrowedBooksCount--;
}
```

```java
public String getEnrollmentDetails() {
    return "Student ID: " + studentId + ", Course ID: " + courseId + ", Status: " + getEnrollmentStatus();
}
```

```java
private void validate() {
    if (amount <= 0) {
        throw new IllegalArgumentException("Payment amount must be greater than zero.");
    }
    if (currency == null || currency.isEmpty()) {
        throw new IllegalArgumentException("Currency cannot be null or empty.");
    }
    if (paymentMethod == null || paymentMethod.isEmpty()) {
        throw new IllegalArgumentException("Payment method cannot be null or empty.");
    }
}
```
