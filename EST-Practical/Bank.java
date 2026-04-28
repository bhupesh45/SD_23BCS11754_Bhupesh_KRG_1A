interface Payment {
  void pay();
}

class Card implements Payment {
  public void pay() {
    System.out.println("Card Payment");
  }
}

class Upi implements Payment {
  public void pay() {
    System.out.println("UPI Payment");
  }
}

class Invoice {
  void generate() {
    System.out.println("Invoice generated");
  }
}

public class Bank {
  public static void main(String[] args) {

    Payment p1 = new Card();
    p1.pay();
    Invoice i1 = new Invoice();
    i1.generate();

    Payment p2 = new Upi();
    p2.pay();
    Invoice i2 = new Invoice();
    i2.generate();
  }
}
